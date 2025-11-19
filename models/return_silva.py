import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from typing import Any, Tuple

def Return(num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, orders:dict[int,list[int]], **unused:Any) -> Tuple[int, float, float, dict[int,tuple[int,int]]]:
    """
    The return policy model of Silva et al

    Inputs:
        - num_aisles: the number of aisles in the instance
        - num_bays: the number of bays per aisle in the instance
        - slot_capacity: the capacity of each slot in the warehouse. The standard is two
        - between_aisle_dist: the distance between consecutive aisles in the warehouse
        - between_bay_dist: the distance between consecutive bays in the warehouse
        - orders: the orders in the specific instance
    
    Outputs:
        - status (int): the Gurobi status
        - distance (float): the final distance found by the model, the model's objective value
        - runtime (float): the model's runtime
        - assignment (dict): the final assignment of products to slots
    """

    # The parameters
    num_prods = num_aisles * num_bays * slot_capacity
    P = range(1, num_prods + 1) # products
    A = range(1, num_aisles + 1) # aisles
    B = range(1, num_bays + 1) # bays
    O = range(1, len(orders) + 1) # orders (total number of orders - whatever the last order number is, add 1)
    Q = orders

    M = between_aisle_dist
    N = between_bay_dist
    C = slot_capacity

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
                if x[a,b,k].X > 0.5:
                    placements.append((a,b,k))

    # Turn it into a DataFrame
    df = pd.DataFrame(placements, columns=["aisle", "bay", "product"])

    assignment = {row['product']: (row['aisle'], row['bay']) for _, row in df.iterrows()}

    return model.Status, model.ObjVal, model.Runtime, assignment

