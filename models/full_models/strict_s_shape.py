import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd
from typing import Tuple, Any

def Strict_S_Shape(num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, orders:dict[int,list[int]], time_limit = 3600, **unused:Any) -> tuple[int, float, float, dict[int:Tuple[int,int]]]:
    """
    The Strict S-Shape model for a warehouse with alternating directional aisles and no transverse

    Inputs:
    - num_aisles: the number of aisles in the warehouse
    - num_bays: the number of bays each aisle is split into
    - slot_capacity: the capacity of each slot (aisle, bay). The standard is two
    - between_aisle_dist: the distance between consecutive aisles
    - between_bay_dist: the distance between consecutive rows
    - orders: the set of orders
    - time_limit: how long the user would like the model to run for

    Outputs:
    - status (int): the final model status
    - distance (float): the distance achieved by the model, taken as the objective value
    - runtime (float): the runtime of the model
    - assignment (dict): the assignment of products to aisles
    """

    all_prods = []
    for i in orders:
        for j in orders[i]:
            all_prods.append(j)
    set_prods = set(all_prods)
    num_prods = len(set_prods)

    if num_prods > num_aisles * num_bays * slot_capacity:
        print(f"num_prods = {num_prods}")
        print(f"num_aisles = {num_aisles}")
        print(f"num_bays = {num_bays}")
        print(f"capacity = {slot_capacity}")
        print(f"num_slots = {num_aisles*num_bays*slot_capacity}")
        print("infeasiblity caused by too many products for the number of slots")
        return 3, np.inf, np.inf, []
    
    gp.setParam('OutputFlag',0)
    gp.setParam('TimeLimit',time_limit)

    N = between_bay_dist
    M = between_aisle_dist

    aisle_capacity = slot_capacity * num_bays
    num_slots = num_aisles * num_bays * slot_capacity
    L = N * (num_bays + 1)

    # generating the direction matrix
    s = np.zeros((num_aisles, num_aisles))
    for i in range(num_aisles):
        for j in range(num_aisles):
            if i == j:
                s[i,j] = 0
            else:
                s[i,j] = (i +1 - j) % 2

    # our sets
    A = range(1, num_aisles + 1)
    B = range(1, num_aisles + 1)
    O = range(1, len(orders) + 1)
    P = range(1, num_slots + 1)

    # the model
    model = gp.Model("Strict_S_Shape")

    # decision variables
    x = model.addVars(A, P, vtype = GRB.BINARY, name = "x") # whether product k is assigned to aisle a
    z = model.addVars(O, A, vtype = GRB.BINARY, name = "z") # if aisle a is visited in order o
    n = model.addVars(O, A, B, vtype = GRB.BINARY, name = "n") # if aisles a and be form a consecutive pair of aisles with picks for order o
    p = model.addVars(O, A, B, vtype = GRB.BINARY, name = "p") # if aisles a and b share a direction and form a pair of aisles with picks for order o
    f = model.addVars(O, A, vtype = GRB.BINARY, name = "f") # if aisle a is the first aisle with a pick for order o
    f_idx = model.addVars(O, ub = num_aisles, vtype = GRB.INTEGER, name = "f_index") # the index of the first aisle with a pick for order o
    F = model.addVars(O, vtype = GRB.BINARY, name = "F") # if the index of the first aisle with a pick is odd for order o
    q = model.addVars(O, A, vtype = GRB.BINARY, name = "q") # if aisle a is the last aisle with a pick for order o
    q_idx = model.addVars(O, ub = num_aisles, vtype = GRB.INTEGER, name = "q_index") # the index of the last aisle with a pick for order o
    Q = model.addVars(O, vtype = GRB.BINARY, name = "Q") # if the index of the last aisle with a pick for order o is odd
    d = model.addVars(O, lb = 0, ub = num_aisles, vtype = GRB.INTEGER, name = "d") # auxiliary variable for defining F
    e = model.addVars(O, lb = 0, ub = num_aisles, vtype = GRB.INTEGER, name = "e") # auxiliary variable for defining Q
    w = model.addVars(O, vtype = GRB.BINARY, name = "w") # auxiliary variable which takes the value 1 iff exactly one aisle contains a pick for order o
    Pen = model.addVars(O, vtype = GRB.BINARY, name = "First_aisle_only_penalty") # an indicator for whether only the first aisle contains a pick (and a horizontal penalty of the 2M needs to be applied)
    u1 = model.addVars(O, vtype = GRB.BINARY, name = "u1") # whether 1 or more aisles have a pick
    u2 = model.addVars(O, vtype = GRB.BINARY, name = "u2") # whether 2 or more aisles have a pick


    # the constraints
    for k in P:
        model.addConstr(
            gp.quicksum(x[a,k] for a in A) == 1,
            name = f"assign_item_{k}_to_a_slot"
        )

    for a in A:
        model.addConstr(
            gp.quicksum(x[a,k] for k in P) <= aisle_capacity,
            name = f"capacity_of_aisle_{a}"
        )
    
    for o in O:
        model.addConstr(
            q_idx[o] == gp.quicksum(a*q[o,a] for a in A),
            name = f"retrieving_the_index_of_the_last_aisle_with_a_pick_for_order_{o}"
        )

        model.addConstr(
            2*e[o] + Q[o] == q_idx[o],
            name = f"if_the_last_aisle_with_a_pick_for_order_{o}_is_odd_indexed"
        )

        model.addConstr(
            gp.quicksum(z[o,a] for a in A) - 1 <= num_aisles * (1-w[o]),
            name = f"w_enforcement_1_order_{o}"
        ) 

        model.addConstr(
            1 - gp.quicksum(z[o,a] for a in A) <= num_aisles * (1-w[o]),
            name = f"w_enforcement_2_order_{o}"
        )

        model.addConstr(
            gp.quicksum(z[o,a] for a in A) <= num_aisles * u1[o],
            name = f"u1_upper_order_{o}"
        )
        
        model.addConstr(
            gp.quicksum(z[o,a] for a in A) >= u1[o],
            name = f"u1_lower_order_{o}"
        )

        model.addConstr(
            gp.quicksum(z[o,a] for a in A) <= 1 + (num_aisles - 1)*u2[o],
            name = f"u2_upper_order_{o}"
        )

        model.addConstr(
            gp.quicksum(z[o,a] for a in A) >= 2*u2[o],
            name = f"u2_lower_order_{o}"
        )

        model.addConstr(
            w[o] == u1[o] - u2[o],
            name = f"enforcing_w_order_{o}"
        )

        model.addConstr(
            Pen[o] <= w[o],
            name = f"first_aisle_only_case_only_occurs_if_exactly_one_aisle_contains_a_pick_in_order_{o}"
        )

        model.addConstr(
            Pen[o] <= z[o,1],
            name = f"first_aisle_only_case_only_occurs_if_first_aisle_contains_a_pick_in_order_{o}"
        )

        model.addConstr(
            Pen[o] >= w[o] + z[o,1] - 1,
            name = f"if_only_one_aisle_contains_a_pick_in_order_{o}_and_the_first_aisle_contains_a_pick_then_apply_penalty"
        )

        model.addConstr(
            f_idx[o] == gp.quicksum(a*f[o,a] for a in A),
            name = f"retrieve_the_index_of_the_first_aisle_with_a_pick_for_order_{o}"
        )

        model.addConstr(
            2*d[o] + F[o] == f_idx[o],
            name = f"if_the_first_aisle_with_a_pick_in_order_{o}_is_odd_or_even_indexed"
        )

        model.addConstr(
            gp.quicksum(q[o,a] for a in A) == 1,
            name = f"exactly_one_aisle_is_the_last_aisle_with_a_pick_for_order_{o}"
        )

        model.addConstr(
            gp.quicksum(f[o,a] for a in A) == 1,
            name = f"exactly_one_aisle_is_the_first_aisle_with_a_pick_for_order_{o}"
        )

        for b in B:
            model.addConstr(
                gp.quicksum(n[o,a,b] for a in range(1,b)) == z[o,b] - f[o,b],
                name = f"each_non-first_visited_aisle_{a}_has_exactly_one_previous_aisle_with_a_pick_for_order_{o}"
            )

        for a in A:
            model.addConstr(
                z[o,a] >= gp.quicksum(x[a,k] for k in orders[o])/aisle_capacity,
                name = f"enter_aisle_{a}_it_it_contains_a_pick_from_order_{o}"
            )

            model.addConstr(
                f[o,a] <= z[o,a],
                name = f"aisle_{a}_can_only_be_the_first_aisle_with_a_pick_for_order_{o}_if_it_contains_a_pick"
            )

            model.addConstr(
                q[o,a] <= z[o,a],
                name = f"aisle_{a}_can_only_be_the_last_aisle_with_a_pick_for_order_{o}_if_it_contains_a_pick"
            )

            model.addConstr(
                gp.quicksum(n[o,a,b] for b in range(a+1, num_aisles + 1)) == z[o,a] - q[o,a],
                name = f"each_non-last_visited_aisle_{a}_has_exactly_one_next_aisle_with_a_pick_for_order_{o}"
            )

            model.addConstr(
                gp.quicksum(z[o,k] for k in range(1, a-1)) <= (1 - f[o,a])*(a-1),
                name = f"if_aisle_{a}_is_the_first_aisle_with_a_pick_for_order_{o}_then_no_previous_aisles_have_picks"
            )

            model.addConstr(
                gp.quicksum(z[o,k] for k in range(a+1, len(A))) <= (1-q[o,a]) * (len(A)-a),
                name = f"if_aisle_{a}_is_the_last_aisle_with_a_pick_for_order_{o}_then_no_further_aisles_will_contain_picks"
            )

            for b in B:
                if b > a:
                    model.addConstr(
                        n[o,a,b] <= z[o,a],
                        name = f"aisle_{a}_can_only_be_involved_in_a_consecutive_pair_of_aisles_with_picks_for_order_{o}_if_it_has_a_pick"
                    )

                    model.addConstr(
                        n[o,a,b] <= z[o,b],
                        name = f"aisle_{b}_can_only_be_involved_in_a_consecutive_pair_of_aisles_with_picks_for_order_{o}_if_it_has_a_pick"
                    )

                    model.addConstr(
                        p[o,a,b] <= n[o,a,b],
                        name = f"only_penalise_aisles_{a}_and_{b}_in_order_{o}_for_having_the_same_direction_if_they_appear_consecutively"
                    )

                    model.addConstr(
                        p[o,a,b] >= n[o,a,b] + s[a-1,b-1] - 1,
                        name = f"if_aisles_{a}_and_{b}_have_same_direction_and_they_appear_consecutively_in_order_{o}_then_penalise"
                    )

    model.setObjective(
        gp.quicksum(L * (gp.quicksum(z[o,a] for a in A) + gp.quicksum(p[o,a,b] for a in A for b in B if b > a) + (1-F[o]) + Q[o]) 
                    + 2 * (q_idx[o] - 1) 
                    + 2 * M * Pen[o] 
                    for o in O),
                    GRB.MINIMIZE
    )

    model.optimize()

    if model.Status == GRB.TIME_LIMIT:
        print(f"Model could not be solved to optimality within the time limit of {time_limit} seconds")

    if model.Status == GRB.INFEASIBLE:
        print("Model is infeasible")
        model.write("infeasible.ilp")

    aisle_assignments_dict = {}

    for aisle in range(1, num_aisles + 1):
        prods = []
        for prod in P:
            if x[aisle,prod].X > 0.5:
                prods.append(prod)
        aisle_assignments_dict[aisle] = prods





    placements = []
    for a in A:
        for k in P:
            if x[a,k].X > 0.5:
                placements.append((int(a),int(k)))

    # Turn it into a DataFrame
    df = pd.DataFrame(placements, columns=["aisle", "product"])

    assignment = {int(row['product']): int(row['aisle'])
              for _, row in df.iterrows()}


    return model.Status, model.ObjVal, model.Runtime, assignment, aisle_assignments_dict