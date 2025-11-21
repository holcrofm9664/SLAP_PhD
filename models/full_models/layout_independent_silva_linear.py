import gurobipy as gp
from gurobipy import GRB
from typing import Tuple
import numpy as np

def Layout_Independent(orders:dict[int,list[int]], distance_matrix:np.ndarray) -> Tuple[int, float, float, dict[int,int]]:
    """
    The layout-independent model of Silva et al

    Inputs:
    - orders: the dictionary of orders used by the model
    - distance_matrix: a numpy array containing the pairwise distances between all slots in the warehouse

    Outputs:
    - status: the status of the gurobi model
    - distance: the distance of the final solution found by the model, taken as its objective value
    - runtime: the runtime of the gurobi model
    - assignments: a dictionary containing the assignments of products to slots
    """

    model = gp.Model("Silva_PolicyIndependent_SLAP")

    # Sets
    P = list(set(k for order in orders for k in order))  # Products
    L = list(range(len(distance_matrix)))  # Locations (slots)
    O = list(range(len(orders)))  # Orders

    # Variables
    y = model.addVars(P, L, vtype=GRB.BINARY, name="y")  # product-to-location assignment
    x = model.addVars(O, L, L, vtype=GRB.BINARY, name="x")  # routing vars per order
    u = model.addVars(O, L, vtype=GRB.CONTINUOUS, name="u")  # MTZ subtour elimination

    # Parameters
    d = distance_matrix  # d[i,j] is distance from slot i to j

    # Objective: minimize total routing distance over all orders
    model.setObjective(
        gp.quicksum(d[i,j] * x[o,i,j] for o in O for i in L for j in L if i != j),
        GRB.MINIMIZE
    )

    # Constraints

    # (2) Each product assigned to one location
    for k in P:
        model.addConstr(gp.quicksum(y[k,l] for l in L) == 1, name=f"assign_{k}")

    # (3) Each location receives at most one product
    for l in L:
        model.addConstr(gp.quicksum(y[k,l] for k in P) <= 1, name=f"capacity_{l}")

    for o, order in enumerate(orders):
        Q_o = order
        for i in L:
            # (4) If i is visited in order o, it's because a product in Q_o is there
            model.addConstr(
                gp.quicksum(x[o,i,j] for j in L if j != i) == gp.quicksum(y[k,i] for k in Q_o),
                name=f"leave_{o}_{i}"
            )
            # (5) If j is visited in order o, it's because a product in Q_o is there
            model.addConstr(
                gp.quicksum(x[o,j,i] for j in L if j != i) == gp.quicksum(y[k,i] for k in Q_o),
                name=f"enter_{o}_{i}"
            )

        # (6) MTZ subtour elimination
        for i in L:
            for j in L:
                if i != j:
                    model.addConstr(
                        u[o,i] - u[o,j] + len(Q_o) * x[o,i,j] <= len(Q_o) - 1,
                        name=f"mtz_{o}_{i}_{j}"
                    )

        # (7) MTZ bounds
        for l in L:
            model.addConstr(u[o,l] >= 0, name=f"u_lb_{o}_{l}")
            model.addConstr(u[o,l] <= len(Q_o) - 1, name=f"u_ub_{o}_{l}")

    #model.setParam("OutputFlag", 0)
    model.optimize()

    # Extract assignment results
    assignment = {}
    if model.Status == GRB.OPTIMAL:
        for k in P:
            for l in L:
                if y[k, l].X > 0.5:
                    assignment[k] = l
    
    return model.Status, model.ObjVal, model.Runtime, assignment