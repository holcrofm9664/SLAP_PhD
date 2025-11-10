import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from typing import Any, Tuple

def S_Shape_Linear(**kwargs:Any) -> Tuple[int,float,float,dict[int,Tuple[int,int]]]:
    """
    The Novel S-Shape model
    
    Keyword Args:
        - num_aisles (int): the number of aisles in the instance
        - num_bays (int): the number of bays per aisle in the instance
        - slot_capacity (int): the capacity of each slot in the warehouse. The standard is two
        - between_aisle_dist (float): the distance between consecutive aisles in the warehouse
        - between_bay_dist (float): the distance between consecutive bays in the warehouse
        - orders (dict): the orders in the specific instance
    
    Outputs:
        - status (int): the Gurobi status
        - distance (float): the final distance found by the model, the model's objective value
        - runtime (float): the model's runtime
        - assignment (dict): the final assignment of products to slots
    
    """
    num_aisles = kwargs["num_aisles"]
    num_bays = kwargs["num_bays"]
    slot_capacity = kwargs["slot_capacity"]
    between_aisle_dist = kwargs["between_aisle_dist"]
    between_bay_dist = kwargs["between_bay_dist"]
    orders = kwargs["orders"]


    model = gp.Model("S-shape")

    model.setParam('TimeLimit', 3600) # 1 hour time limit

    M = between_aisle_dist
    N = between_bay_dist
    prod_num = num_aisles*num_bays*slot_capacity

    A = range(1, num_aisles + 1)
    B = range(1, num_bays + 1)
    P = range(prod_num)
    C = slot_capacity
    Q = orders
    O = range(len(Q))

    x = model.addVars(A, B, P, vtype=GRB.BINARY, name = "x") # indicators if product k is in slot (a,b)
    z = model.addVars(O, A, vtype = GRB.BINARY, name = "z") # indicators if aisle a contains an ordered product from order O
    v = model.addVars(O, lb = 1, ub=num_aisles, vtype=GRB.CONTINUOUS, name = "v") # the last aisle reached for order o
    is_odd = model.addVars(O, vtype = GRB.BINARY, name = "is_odd") # a variable for if there are an odd number of aisles
    w = model.addVars(O, lb = 1, ub = num_bays, vtype=GRB.CONTINUOUS, name="last_bay") # the last row of the last aisle
    t = model.addVars(O, vtype=GRB.INTEGER, name = "t") # an auxiliary variable for seeing if there are an odd or even number of aisles used
    d = model.addVars(O, lb = 0, ub = num_bays, vtype = GRB.CONTINUOUS, name="d") # an auxiliary variable to linearise the objective
    delta = model.addVars(O, A, vtype=GRB.BINARY, name="delta") # an auxiliary variable to deal with the w_o problem
    s = model.addVars(O, A, B, vtype = GRB.BINARY, name = "s") # if order o has a pick in slot (a,b)

    model.setParam('OutputFlag', 0)
    
    # maximum slot capacity

    #model.setParam(GRB.Param.cutoff, heuristic_solution_value)

    for a in A:
        for b in B:
            model.addConstr(gp.quicksum(x[a,b,k] for k in P) <= C,
            name = f"capacity_of_slot_{a}_{b}"
            )

    # assign products

    for k in P:
        model.addConstr(
            gp.quicksum(x[a,b,k] for a in A for b in B) == 1,
            name = f"assign_product_{k}"
        )

    # enforcing z variable

    for o in O:
        for a in A:
            model.addConstr(
                gp.quicksum(s[o,a,b] for b in B) <= len(B)*z[o,a],
                name = f"z_ub_{o}_{a}"
            )

            model.addConstr(
                gp.quicksum(s[o,a,b] for b in B) >= z[o,a],
                name = f"z_lb_{o}_{a}"
            )

            for b in B:
                model.addConstr(
                    s[o,a,b] <= z[o,a],
                    name = f"s_less_z_{o}_{a}_{b}"
                )

    # last aisle to be entered for order o

    for o in O:
        for a in A:
            model.addConstr(
                v[o] >= a * z[o,a],
                name = f"last_aisle_entered_order_{o}"
            )

    # find if there are an odd number of aisles containing picks for order o

    for o in O:
        model.addConstr(
            gp.quicksum(z[o,a] for a in A) == 2*t[o] + is_odd[o],
            name = f"check_if_odd_number_of_aisles_order_{o}"
        )

    # defining S

    for o in O:
        for a in A:
            for b in B:
                model.addConstr(
                    gp.quicksum(x[a,b,k] for k in Q[o]) <= len(Q[o])*s[o,a,b],
                    name = f"s_ub_{o}_{a}_{b}"
                )

                model.addConstr(
                    gp.quicksum(x[a,b,k] for k in Q[o]) >= s[o,a,b],
                    name = f"s_lb_{o}_{a}_{b}"
                )

    
    # find the last row containing a product in the last aisle of order o

    for o in O:
        for a in A:
            for b in B:
                model.addGenConstrIndicator(
                    delta[o,a], 1, w[o] >= b*s[o,a,b],
                    name = f"last_row_ind_{o}_{a}_{b}"
                )

    # the linearisation constraints

    for o in O:
        model.addGenConstrIndicator(
            is_odd[o], 1, d[o] == w[o],
            name = f"condition_if_odd_{o}"
        )

        model.addGenConstrIndicator(
            is_odd[o], 0, d[o] == 0,
            name = f"condition_if_even_{o}"
        )

    # constraints on auxiliary variable delta

    for o in O:
        model.addConstr(
            gp.quicksum(a * delta[o,a] for a in A) == v[o],
            name = f"delta_constr_1_order_{o}"
        )

        model.addConstr(
            gp.quicksum(delta[o,a] for a in A) == 1,
            name = f"delta_constr_2_order_{o}"
        )

    for o in O:
        for a in A:
            model.addConstr(
                delta[o,a] <= z[o,a],
                name = f"last_aisle_fix_{o}_{a}"
            )

    model.setObjective(
        gp.quicksum(
        2 * M * (v[o]-1) + # cross_aisle_distance
        (len(B) + 1) * N * (gp.quicksum(z[o,a] for a in A) - is_odd[o]) + # within-aisle distance (even number of aisles)
        2 * N * d[o] # the backtracking
        for o in O),
        GRB.MINIMIZE
    )

    model.optimize()

    # Print all occupied slots
    placements = []
    for a in A:
        for b in B:
            for k in P:
                if x[a, b, k].X > 0.5:
                    placements.append((a, b, k))

    
    # Turn it into a DataFrames
    df = pd.DataFrame(placements, columns=["aisle", "bay", "product"])

    assignment = {row['product']: (row['aisle'], row['bay']) for _, row in df.iterrows()}

    return model.Status, model.ObjVal, model.Runtime, assignment
