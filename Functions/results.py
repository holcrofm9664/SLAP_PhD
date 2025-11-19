import pandas as pd
import numpy as np
from typing import Any, Tuple
from dataclasses import dataclass
from Functions.orders_generation import generate_orders
from Models.strict_s_shape import Strict_S_Shape

def check_if_larger(instance1:list[int], instance2:list[int]) -> bool:
    """
    Checks whether an instance is at least as large as another instance, whereby to be larger than another instance 
    means that every parameter is at least as large as the corresponding parameter in the other instance.
    
    Inputs:
    - instance1: the first instance, represented by its number of aisles, number of bays, number of orders and size of orders
    - instance2: the second instance, represented by its number of aisles, number of bays, number of orders and size of orders

    Outputs:
    - a boolean value indicating whether or not the first instance is larger than the second instance
    """
    
    for i in range(len(instance1)):
        if instance1[i] < instance2[i]:
            return False
        
    return True

def size_check(instance:list[int], stored_instances:dict[int,list[int]]) -> int:
    """
    Checks if an instance is larger than any of the stored instances, for use in determining whether gurobi should attempt to solve it

    Inputs:
    - instance: the instance we are testing, given as a list of its parameters
    - stored_instances: the instances which we have been unable to solve so far, stored as lists of their parameters

    Outputs:
    - a binary, indicating whether the instance should be solved
    """

    for inst in stored_instances:
        val = check_if_larger(instance, stored_instances[inst])
        if val == True:
            return 0 # do not solve, as it is larger than at least one instance
    return 1

def solve_all(A_vals:list[int], B_vals:list[int], O_vals:list[int], Q_vals:list[int], slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, num_trials:int, **unused:Any):
    
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
            for i in range(num_trials):
                orders = generate_orders(instances[inst][2], instances[inst][3], instances[inst][0]*instances[inst][1]*slot_capacity, seed = seed)
                status, distance, runtime, assignments = Strict_S_Shape(instances[inst][0], instances[inst][1], slot_capacity, between_aisle_dist, between_bay_dist, orders)
                seed += 1
                if status != 2:
                    stored_instances.update({count:instances[inst]})
                    count += 1
                    break
                else:
                    orders_dict.update({orders_count:orders})
                    orders_count += 1
                    new_row = {"aisles":instances[inst][0], "bays":instances[inst][1], "num_orders":instances[inst][2], "order_size":instances[inst][3], "distance":distance, "runtime":runtime}
                    df = pd.concat([df, pd.DataFrame([new_row])],ignore_index=True)

    return df, orders_dict