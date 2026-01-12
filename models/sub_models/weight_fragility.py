import numpy as np
import gurobipy as gp
from gurobipy import GRB
from typing import Tuple
from collections import Counter

def weight_fragility(prods_in_aisle:list[int], orders:dict[int,list[int]], crushing_array:np.ndarray[int], cluster_assignments:list[int], num_bays:int, slot_capacity:int, cluster_max_distance:int, aisle:int, slot_assignments_dict:dict[int:tuple[int,int]], output_flag:bool) -> Tuple[int, float, list[tuple[int,int]]]:
    """
    The second stage model which assigns products to bays within one aisle (to which they were assigned in the first stage). 
    
    Inputs
    - prods_in_aisle: the products assigned to the aisle we are optimising
    - orders: the set of orders used to assign products. These are needed as a product can only be crushed by another product if they are in the same order
    - crushing_array: an array of size num_products x num_products, showing if the second product can crush the first (1) or not (0)
    - cluster_assignments: a list giving which cluster each product belongs to. This could be the aisle the product belongs to in the destination shop, or something more general
    - num_bays: the number of bays the aisle is split into
    - slot_capacity: the capacity of one bay, the standard being 2
    - cluster_max_distance: the maximum number of bays apart two items belonging to the same cluster should be placed.
    - aisle: the aisle we are optimising
    - slot_assignments_dict: the dictionary of assignments of products to slots 
    - output_flag: whether the user wishes to see full output of model solving

    Outputs:
    - status: whether a feasible solution was found
    - objective value: the number of crushing events which would have occurred had the assignment been used on the set of orders
    - runtime: the model runtime
    - slot_assignments_dict: the updated assignments dictionary, now containing products assigned to this aisle
    """

    # initialising the model
    model = gp.Model("weight_fragility")

    model.setParam("OutputFlag", output_flag)
    c = {}
    print(cluster_assignments)

    for i in range(1, len(cluster_assignments) + 1):
        c[i] = cluster_assignments[i-1]

    cluster_sizes = Counter(c.values())

    max_cluster_size = max(cluster_sizes.values())

    if max_cluster_size >= num_bays/2*slot_capacity: # a safety clause such that if more than half of items are in the same cluster it does not cause infeasibility
        cluster_max_distance = 100

    num_products = num_bays * slot_capacity

    while len(c) < num_products:
        c.update({len(c)+1:0})

    # sets
    B = range(1, num_bays + 1)
    I = prods_in_aisle
    Q = orders
    O = list(orders.keys())

    # variables
    x = model.addVars(I, B, vtype = GRB.BINARY, name = "x") # assignment of products to slots
    p = model.addVars(I, O, vtype = GRB.BINARY, name = "p") # whether an item is crushed and a penalty applied

    # assignment constraint
    for i in I:
        model.addConstr(
            gp.quicksum(x[i,b] for b in B) == 1,
            name = f"assign_product_{i}_to_a_bay"
        )

        # constraints for ensuring that similar products are placed close to each other
        for j in I:
            if j != i:    
                if c[i] == c[j]:
                    model.addConstr(
                        gp.quicksum(b*x[i,b] for b in B) - gp.quicksum(b*x[j,b] for b in B) <= cluster_max_distance,
                        name = f"upper_bound_on_distance_between_products_{i}_and_{j}"
                    )

    for b in B:
        model.addConstr(
            gp.quicksum(x[i,b] for i in I) <= slot_capacity,
            name = f"capacity_of_bay_{b}"
        )

    # constraints relating to crushing
    for o in O:
        for i in Q[o]:
            for b in B:
                further_aisles = range(b+1,len(B))
                model.addConstr(
                    p[i,o] >= x[i,b] + gp.quicksum(x[j,k]*crushing_array[i-1,j-1] for k in further_aisles for j in Q[o] if j != i)/len(B) - 1,
                    name = f"prod_{i}_crushed_if_in_bay_{b}_and_a_future_bay_contains_a_product_able_to_crush_it_in_order_{o}"
                )
                
                
    # objective
    model.setObjective(
        gp.quicksum(p[i,o] for i in I for b in B for o in O),
        GRB.MINIMIZE
    )

    model.optimize()

    if model.Status != 2:
        model.computeIIS()
        model.write("infeasible.ilp")

    if aisle % 2 == 1:
        for i in I:
            for b in B:
                if x[i,b].X > 0.5:
                    slot_assignments_dict[i] = (aisle, b)
    elif aisle % 2 == 0:
        for i in I:
            for b in B:
                if x[i,b].X > 0.5:
                    slot_assignments_dict[i] = (aisle, len(B)-b+1)


    return model.Status, model.ObjVal, model.Runtime, slot_assignments_dict
