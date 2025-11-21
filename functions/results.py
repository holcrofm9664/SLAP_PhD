import pandas as pd
from typing import Any, Iterable, Tuple
from functions.orders_generation import generate_orders
from models.full_models.strict_s_shape import Strict_S_Shape

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



def solve_all(instances:Iterable[list[int]], slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, num_trials:int, **unused:Any) -> Tuple[pd.DataFrame, dict[int,dict[int]]]:
    """
    Runs a model on a set of instances for multiple trials, avoiding testing instances with a high likelihood of timeout
    
    Inputs:
    - instances: the combinations of input parameters we wish to test
    - slot_capacity: the capacity of a slot in the warehouse. The standard is 2
    - between_aisle_dist: the distance between consecutive aisles in the warehouse
    - between_bay_dist: the distance between consecutive bays in the warehouse
    - num_trials: the number of times we wish to test each instance

    Outputs:
    - a dataframe including input parameters, final distance and runtimes
    - a pickle file of the orders used in each trial
    """                   

    data = []
    stored_instances = []
    orders_dict = {}
    count = 0
    seed = 1


    for inst in instances:
        if any(check_if_larger(list(inst), instance) for instance in stored_instances) or len(stored_instances) == 0:
            for i in range(num_trials):
                instance = list(inst)
                orders = generate_orders(instance[2], instance[3], instance[0]*instance[1]*slot_capacity, seed = seed)
                status, distance, runtime, _ = Strict_S_Shape(instance[0], instance[1], slot_capacity, between_aisle_dist, between_bay_dist, orders)
                seed += 1
                if status != 2:
                    stored_instances.append(instance)
                    count += 1
                    break
                else:
                    orders_dict.update({count:orders})
                    data.append({"aisles":instance[0], "bays":instance[1], "num_orders":instance[2], "order_size":instance[3], "distance":distance, "runtime":runtime})
    
    df = pd.DataFrame(data)

    return df, orders_dict