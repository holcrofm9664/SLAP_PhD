import gurobipy as gp
from gurobipy import GRB
import numpy as np
from typing import Tuple

def solve_single_tsp(order:list[int], between_product_distance_matrix:np.ndarray[int,int]) -> float:
    """
    Solves a TSP for a single order given fixed product assignments. Node 0 is taken as being the input/output

    Inputs:
    - order: a single order, used to achieve the aisle assignments
    - between_product_distance_matrix: a numpy array containing the pairwise distances between pairs of slots, including the door

    Outputs:
    - distance: the route distance for this order
    """

    M = between_product_distance_matrix

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


def total_distance_for_all_orders(orders:dict[int,list[int]], between_product_distance_matrix:float) -> Tuple[float,dict[int,float]]:
    """
    Calculates the routing distance for all orders and sums them together to obtain the total distance

    Inputs: 
    orders: the dictionary of all orders used to achieve the aisle assignments
    between_product_distance_matrix: a numpy array containing the pairwise distances between pairs of slots, including the door

    Outputs:
    - total: the total distance travelled during picker routing over all orders
    - per_order: the distance travelled for each order
    """

    total = 0
    per_order = {}

    for order_id, order_list in orders.items():
        d = solve_single_tsp(order_list, between_product_distance_matrix)
        per_order[order_id] = d
        total += d

    return total, per_order
