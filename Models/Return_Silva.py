# Return Policy Function

def Return(Orders: dict[int:list], Prod_Num: int, Aisles: int, Bays: int, Aisle_Dist: float, Bay_Dist: float, Slot_Capacity: int):
    """
    inputs:
        - Orders: A dictionary, where the keys are the order number, and the value is a list of the ordered products
        - Prod_Num: The number of products stored in the warehouse. We can reasonably set this to the number of slots in the warehouse, and when there are fewer products than slots the remainder will essentially be dummy products which are never ordered
        - Aisles: The number of aisles
        - Bays: The number of bays per aisle
        - Aisle_Dist: The distance between two consecutive aisles
        - Bay_Dist: The distance between two consecutive bays
    """

    import gurobipy as gp
    from gurobipy import GRB
    import pandas as pd

    # The parameters
    P = range(Prod_Num) # products
    A = range(1, Aisles+1) # aisles
    B = range(1, Bays+1) # bays
    O = range(len(Orders)) # orders (total number of orders - whatever the last order number is, add 1)
    Q = Orders

    N = Bay_Dist
    M = Aisle_Dist
    C = Slot_Capacity

    # The model

    model = gp.Model("SLAP_Return")
    
    # The variables

    x = model.addVars(A, B, P, vtype=GRB.BINARY, name="x") # binary variable, if product k is in slot (a,b)
    z = model.addVars(O, A, vtype=GRB.BINARY, name="z") # indicator if there is a product in aisle a for order o
    f = model.addVars(O, A, vtype=GRB.INTEGER, name = "f") # the furthest bay to contain a pick in aisle a for order o
    last_aisle = {o: model.addVar(vtype = GRB.INTEGER, name = "last_aisle_order_{o}") for o in O} # the last aisle we enter, for use in cross-aisle distance

    # The constraints

    # max C items per slot (when this is two, we have one either side of the aisle)

    for a in A:
        for b in B:
            model.addConstr(
                gp.quicksum(x[a,b,k] for k in P) <= C,
                name = f"max_two_products_for_slot_{a}_{b}"
            )

    # exactly one slot per item

    for k in P:
        model.addConstr(
            gp.quicksum(x[a,b,k] for a in A for b in B) == 1,
            name = f"product_{k}_assigned_to_exactly_one_slot"
        )

    # ensure that an aisle containing a product is entered

    for o in O:
        for a in A:
            model.addConstr(
                max(B)*z[o,a] >= f[o,a],
                name = f"enter_aisle_{a}_order_{o}"
            )

            # last aisle for order o

            model.addConstr(
                last_aisle[o] >= a * z[o,a],
                name = f"last_aisle_{a}_order_{o}"
            )

            # ensure z[o,a] is positive when there is a product in an aisle

            model.addConstr(
                z[o,a] >= gp.quicksum(x[a,b,k] for b in B for k in Q[o]) / len(Q[o]),
                name = f"z_def_{o}_{a}"
            )

            # determine the furthest row which has a required product for each aisle for each order

            for b in B:
                for k in Q[o]:
                    model.addConstr(
                        f[o,a] >= b*x[a,b,k],
                        name = f"furthest_row_aisle_{a}_order_{o}"
                    )

    # Set the model objective

    model.setObjective(
    gp.quicksum(2 * N * f[o,a] * z[o,a] for o in O for a in A)  # Aisle (row) distance
    + gp.quicksum(2 * M * (last_aisle[o]-1) for o in O),            # Cross-aisle distance
    GRB.MINIMIZE
    )

    # optimise the model

    model.optimize()

    # Build a flat list (aisle, bay, product) for every occupied slot
    placements = []
    for a in A:
        for b in B:
            for k in P:
                if x[a, b, k].X > 0.5:
                    placements.append((a, b, k))

    # Turn it into a DataFrame
    df = pd.DataFrame(placements, columns=["aisle", "bay", "product"])

    assignment = {row['product']: (row['aisle'], row['bay']) for _, row in df.iterrows()}

    return model.Status, model.ObjVal, model.Runtime, assignment

