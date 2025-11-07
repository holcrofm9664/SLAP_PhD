import pandas as pd
from Functions.orders_generation import generate_orders
from Functions.instance_generation import generate_single_instance
from typing import Callable

def test_model(model:Callable, A:list, B:list, O:list, Q:list, num_trials:int, slot_capacity:int) -> pd.df:
    """
    A function which runs one model a set number of times on all combinations of selected input parameters, 
    and generates a dataframe with the distances and runtimes achieved.

    Inputs:
    - model: the chosen model we wish to test
    - A: a list containing the different aisle numbers which will be tested
    - B: a list containing the different bay numbers which will be tested
    - O: a list containing the different numbers of orders which will be tested
    - Q: a list containing the different order sizes which will be tested
    - num_trials: the number of times we wish to run the model on each instance
    - slot_capacity: the capacity of each slot in the warehouse. The standard is two

    Output:
    - df: a pandas dataframe of the results, where each row corresponds the the input parameters of each 
    instances alongside the average distance achieved and the average runtime
    """
    
    avg_distances = []
    avg_runtimes = []
    aisles = []
    bays = []
    order_numbers = []
    order_sizes = []
    for a in A:
        for b in B:
            for o in O:
                for q in Q:
                    distances = []
                    runtimes = []
                    for i in range(num_trials):
                        num_prods = a * b * slot_capacity
                        orders = generate_orders(o, q, num_prods)
                        instance = generate_single_instance(a, b, slot_capacity, 1, 1, orders)
                        _, distance, runtime, _ = model(**instance)
                        distances.append(distance)
                        runtimes.append(runtime)
                    avg_distances.append(round(sum(distances)/num_trials,3))
                    avg_runtimes.append(round(sum(runtimes)/num_trials,3))
                    aisles.append(a)
                    bays.append(b)
                    order_numbers.append(o)
                    order_sizes.append(q)
    
    df_dict = {}
    df_dict["aisles"] = aisles
    df_dict["bays"] = bays
    df_dict["num_orders"] = order_numbers
    df_dict["order_size"] = order_sizes
    df_dict["avg_distance"] = avg_distances
    df_dict["avg_runtime"] = avg_runtimes

    df = pd.DataFrame(df_dict)
    return df