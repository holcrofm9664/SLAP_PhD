import gurobipy as gp
from gurobipy import GRB

# creating our model

def S_Shape_Silva_Linear(num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, orders: dict[int:list]):

    import pandas as pd

    model = gp.Model("s_shape_sila")

    # adding ranges

    M = between_aisle_dist
    N = between_bay_dist
    Q = orders
    A = range(1, num_aisles + 1)
    B = range(1, num_bays + 1)
    P = range(1, num_aisles*num_bays*slot_capacity + 1)
    O = range(1, len(orders) + 1)

    # adding variables

    y = model.addVars(A, B, P, vtype = GRB.BINARY, name = "y") # the assignment variables
    f = model.addVars(O, A, lb = 0, ub = len(B), vtype = GRB.INTEGER) # the furthest row containing a pick for aisle a
    z = model.addVars(O, A, vtype = GRB.BINARY, name = "z") # if we enter aisle a for order o
    v = model.addVars(O, A, vtype = GRB.BINARY, name = "v") # if aisle a is the last aisle used for order o
    k_aux = model.addVars(O, lb = 0, ub = len(A)/2, vtype = GRB.INTEGER, name = "k") # an auxiliary variable for checking if there are an odd number of aisles
    S = model.addVars(O, vtype = GRB.BINARY, name = "S") # if there are an odd number of aisles for order o
    w = model.addVars(O, A, vtype = GRB.BINARY, name = "w") # an auxiliary variable for linearisation
    x = model.addVars(O, A, lb = 0, vtype = GRB.INTEGER, name = "x") # auxiliary variable for second round of linearisation

    model.setParam('TimeLimit', 3600) # 1 hour time limit
    model.setParam('OutputFlag', 0)

    # adding constraints

    for k in P:
        model.addConstr(
            gp.quicksum(y[a,b,k] for a in A for b in B) == 1,
            name = f"assignment_of_product_{k}"
        )

    for a in A:
        for b in B:
            model.addConstr(
                gp.quicksum(y[a,b,k] for k in P) <= slot_capacity,
                name = f"capacity_of_slot_{a}_{b}"
            )

    for o in O:
        for a in A:
            model.addConstr(
                z[o,a] >= gp.quicksum(y[a,b,k] for k in Q[o] for b in B) / len(P)
            )

    for o in O:
        for a in A:
            model.addConstr(
                z[o,a] <= gp.quicksum(y[a,b,k] for k in Q[o] for b in B),
                    name = f"z_upper_bound_{o}_{a}"
            )

    for o in O:
        for a in A:
            model.addConstr(v[o,a] <= z[o,a])
            model.addConstr(v[o,a] <= 1 - gp.quicksum(z[o,a2] for a2 in A if a2 > a))
            model.addConstr(v[o,a] >= z[o,a] - gp.quicksum(z[o,a2] for a2 in A if a2 > a))
        model.addConstr(gp.quicksum(v[o,a] for a in A) == 1)

    # probably the worst constraint
    
    for o in O:
        for a in A:
            for b in B:
                for k in Q[o]:
                    model.addConstr(
                        f[o,a] >= b * y[a,b,k],
                        name = f"max_bay_used_{o}_{a}_{b}_{k}"
                    )

                
    for o in O:
        for a in A:
            model.addConstr(
                f[o,a] <= len(B) * z[o,a],
                name = f"enter_aisle_{a}_order_{o}"
            )

        model.addConstr(
            gp.quicksum(z[o,a] for a in A) == 2 * k_aux[o] + S[o],
            name = f"odd_number_of_aisles_order_{o}"
        )


    # first set of linearisation constraints

    for o in O:
        for a in A:
            model.addConstr(
                w[o,a] <= S[o],
                name = f"linearisation_constr_1_{o}_{a}"
            )

            model.addConstr(
                w[o,a] <= v[o,a],
                name = f"linearisation_constr_2_{o}_{a}"
            )

            model.addConstr(
                w[o,a] >= S[o] + v[o,a] - 1,
                name = f"linearisation_constr_3_{o}_{a}"
            )

    # second round of linearisation constraints

    for o in O:
        for a in A:
            model.addConstr(
                x[o,a] <= f[o,a],
                name = f"lin_2_constr_1_{o}_{a}"
            )

            model.addConstr(
                x[o,a] >= f[o,a] - len(B)*(1-w[o,a]),
                name = f"lin_2_constr_2_{o}_{a}"
            )

            model.addConstr(
                x[o,a] <= len(B) * w[o,a],
                name = f"lin_2_constr_3_{o}_{a}"
            )


    model.setObjective(
        gp.quicksum(
            gp.quicksum(2 * M * v[o,a] * (a - 1) for a in A) + # cross-aisle distance
            gp.quicksum(N * (len(B) + 1) * z[o,a] + 2 * N * x[o,a] for a in A) - # distance of aisles fully-traversed
            N * (len(B) + 1) * S[o]
        for o in O),
        GRB.MINIMIZE
    )

    model.optimize()

    placements = []
    for a in A:
        for b in B:
            for k in P:
                if y[a, b, k].X > 0.5:
                    placements.append((a, b, k))

    
    # Turn it into a DataFrame
    df = pd.DataFrame(placements, columns=["aisle", "bay", "product"])

    assignment = {row['product']: (row['aisle'], row['bay']) for _, row in df.iterrows()}

    return model.Status, model.ObjVal, model.Runtime, assignment