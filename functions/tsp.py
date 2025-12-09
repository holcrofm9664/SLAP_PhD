import gurobipy as gp
from gurobipy import GRB
import numpy as np

def solve_single_tsp(order, M):
    """
    Solve a TSP for a single order and return the optimal distance.
    Node 0 is the door.
    """

    nodes = [0] + order
    n = len(nodes)

    m = gp.Model("tsp_single")
    m.Params.OutputFlag = 0  # silent

    # Binary variables: x[i,j] = 1 if route goes i -> j
    x = m.addVars(nodes, nodes, vtype=GRB.BINARY, name="x")

    # MTZ variables
    u = m.addVars(nodes, vtype=GRB.CONTINUOUS, lb=0, ub=n-1, name="u")

    # Objective: minimise total distance
    m.setObjective(
        gp.quicksum(M[i,j] * x[i,j] for i in nodes for j in nodes),
        GRB.MINIMIZE
    )

    # Degree constraints
    for i in nodes:
        m.addConstr(gp.quicksum(x[i,j] for j in nodes if j != i) == 1)
        m.addConstr(gp.quicksum(x[j,i] for j in nodes if j != i) == 1)

    # No self-loops
    for i in nodes:
        m.addConstr(x[i,i] == 0)

    # MTZ subtour elimination (skip node 0)
    for i in nodes[1:]:
        for j in nodes[1:]:
            if i != j:
                m.addConstr(u[i] - u[j] + (n - 1)*x[i,j] <= n - 2)

    m.optimize()

    # extract total distance
    total_distance = sum(
        M[i,j] for i in nodes for j in nodes if x[i,j].X > 0.5
    )

    return total_distance


def total_distance_for_all_orders(orders, M):
    """
    Compute minimal picking route distance for each order
    and return the total distance across all orders.
    """

    total = 0
    per_order = {}

    for order_id, order_list in orders.items():
        d = solve_single_tsp(order_list, M)
        per_order[order_id] = d
        total += d

    return total, per_order
