import pandas as pd
import numpy as np
from Functions.orders_generation import generate_orders
from Models.strict_s_shape import Strict_S_Shape

def check_if_larger(instance1, instance2):
    for i in range(len(instance1)):
        if instance1[i] < instance2[i]:
            return False
        
    return True

def size_check(instance, stored_instances):
    for inst in stored_instances:
        val = check_if_larger(instance, stored_instances[inst])
        if val == False:
            return 0 # do not solve
    return 1

def solve_all(A_vals, B_vals, O_vals, Q_vals, slot_capacity, between_aisle_dist, between_bay_dist, num_trials, **unused):
    
    # generate the instances
    instances = {}
    count = 1
    for a in A_vals:
        for b in B_vals:
            for o in O_vals:
                for q in Q_vals:
                    instances.update({count:[a,b,o,q]})
                    count += 1
                    
    
    df = pd.DataFrame()
    stored_instances = {}
    orders_dict = {}
    count = 1
    orders_count = 0
    seed = 1


    for inst in instances:
        val = size_check(instances[inst], stored_instances)
        if val == 1:
            distances = []
            runtimes = []
            for i in range(num_trials):
                orders = generate_orders(instances[inst][2], instances[inst][3], instances[inst][0]*instances[inst][1]*slot_capacity, seed = seed)
                status, distance, runtime, assignments = Strict_S_Shape(instances[inst][0], instances[inst][1], slot_capacity, between_aisle_dist, between_bay_dist, orders)
                seed += 1
                if status != 2:
                    stored_instances.update({count:instances[inst]})
                    count += 1
                    break
                else:
                    distances.append(distance)
                    runtimes.append(runtime)
                    orders_dict.update({orders_count:orders})
                    orders_count += 1
            new_row = {"aisles":instances[inst][0], "bays":instances[inst][1], "num_orders":instances[inst][2], "order_size":instances[inst][3], "avg_distance":np.mean(distances), "avg_runtime":np.mean(runtimes)}
            df = pd.concat([df, pd.DataFrame([new_row])],ignore_index=True)
            orders_count += 1

    return df, orders_dict
    

A_vals = [1,3,5]
B_vals = [5,10]
O_vals = [1,3,5]
Q_vals = [5,10]
slot_capacity = 2
between_aisle_dist = 1
between_bay_dist = 1
num_trials = 2

instance = {"A_vals":A_vals,
            "B_vals":B_vals,
            "O_vals":O_vals,
            "Q_vals":Q_vals,
            "slot_capacity":slot_capacity,
            "between_aisle_dist":between_aisle_dist,
            "between_bay_dist":between_bay_dist,
            "num_trials":num_trials}


df, orders_dict = solve_all(**instance)

print(df)