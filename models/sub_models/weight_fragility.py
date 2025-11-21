import gurobipy as gp
from gurobipy import GRB
from typing import Tuple
from collections import Counter

def weight_fragility(orders:dict[int,list[int]], prod_features:dict[str,list[int]], num_bays:int, slot_capacity:int) -> Tuple[int, float, list[tuple[int,int]]]:
    
    # initialising the model
    model = gp.Model("weight_fragility")

    weight_vals = prod_features["prod_heavy"]
    aisle_vals = prod_features["prod_aisle"]

    max_cluster_size = Counter(aisle_vals).most_common(1)[0][1]

    h = {}
    a = {}

    for i in range(1, len(weight_vals)+1):
        h[i] = weight_vals[i-1]
        a[i] = aisle_vals[i-1]
    print(h)
    print(a)
    fragile_list = prod_features["prod_fragile"]
    fragile_prods = [i+1 for i, f in enumerate(fragile_list) if f == 1]

    num_products = num_bays * slot_capacity

    # sets
    B = range(1, num_bays + 1)
    I = range(1, num_products + 1)
    Q = orders
    O = range(1, len(Q) + 1)

    # variables
    x = model.addVars(I, B, vtype = GRB.BINARY, name = "x") # assignment of products to slots
    p = model.addVars(I, O, vtype = GRB.BINARY, name = "p") # whether an item is crushed and a penalty applied
    z = model.addVars(I, I, vtype = GRB.INTEGER, name = "z") # auxiliary variable to define an absolute difference

    for i in I:
        model.addConstr(
            gp.quicksum(x[i,b] for b in B) == 1,
            name = f"assign_product_{i}_to_a_bay"
        )

        for j in I:
            if j > i:
                if a[i] == a[j]:
                    model.addConstr(
                        z[i,j] >= gp.quicksum(b*x[i,b] for b in B) - gp.quicksum(b*x[j,b] for b in B),
                        name = f"lower_bound_on_z_for_products_{i}_and_{j}"
                    )

                    model.addConstr(
                        z[i,j] <= -gp.quicksum(b*x[i,b] for b in B) + gp.quicksum(b*x[j,b] for b in B),
                        name = f"upper_bound_on_z_for_products_{i}_and_{j}"
                    )

                    model.addConstr(
                        z[i,j] <= max_cluster_size/2,
                        name = f"enforce_a_maximal_distance_between_items_in_one_cluster_items_{i}_{j}"
                    )

    for b in B:
        model.addConstr(
            gp.quicksum(x[i,b] for i in I) <= slot_capacity,
            name = f"capacity_of_bay_{b}"
        )

    for o in O:
        for i in fragile_prods:
            for b in B:
                model.addConstr(
                    p[i,o] <= x[i,b],
                    name = f"penalty_only_applied_if_product_{i}_assigned_to_bay_{b}_for_order_{o}"
                )

                further_bays = range(b+1, len(B))
                model.addConstr(
                    p[i,o] <= gp.quicksum(x[k,b]*h[k] for k in further_bays if k in Q[o])/len(B),
                    name = f"penalty_only_applied_for_product_{i}_if_further_bay_contains_a_heavy_product_for_order_{o}"
                )

                model.addConstr(
                    p[i,o] >= gp.quicksum(x[k,b]*h[k] for k in further_bays)/len(B) + x[i,b] - 1,
                    name = f"if_fragile_product_{i}_stored_in_bay_b_and_heavy_product_stored_in_further_bay_for_order_{o}_apply_penalty"
                )
    

    # objective
    model.setObjective(
        gp.quicksum(
            gp.quicksum(p[i,o] for i in I)
            for o in O
        ),
        GRB.MINIMIZE
    )

    model.optimize()
    
    placements = []
    for i in I:
        for b in B:
            print(x[i,b])
            if x[i,b].X > 0.5:
                placements.append((int(i),int(b)))

    return model.Status, model.ObjVal, placements
                
