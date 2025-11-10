import pandas as pd
from Functions.orders_generation import generate_orders
from Functions.instance_generation import generate_single_instance
from typing import Callable

def test_model(model:Callable, A:list, B:list, O:list, Q:list, num_trials:int, slot_capacity:int) -> pd.DataFrame:
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


def test_ABO(A, B, O, Q_values, df, trials, model):
    for q in Q_values:
        if q > 2*A*B:
            break
        orders = generate_orders(O, q, A*B*2)
        instance = generate_single_instance(A, B, 2, 1, 1, orders)
        runtimes = []
        distances = []
        for i in range(trials):
            result = model(**instance)
            if result[0] != 2:
                return df
            else:
                runtimes.append(result[2])
                distances.append(result[1])
        avg_runtime = sum(runtimes)/trials
        avg_distance = sum(distances)/trials
        new_row = {"aisles":A, "bays":B, "num_orders":O, "order_size":q, "avg_distance":avg_distance, "avg_runtime":avg_runtime}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index = True)
    return df
    

def test_AB(A, B, O_values, Q_values, df, trials, model):
    for o in O_values:
        df_len = len(df)
        df = test_ABO(A, B, o, Q_values, df, trials, model)
        if len(df) == df_len:
            break
    return df


def test_A(A, B_values, O_values, Q_values, df, trials, model):
    for b in B_values:
        df_len = len(df)
        df = test_AB(A, b, O_values, Q_values, df, trials, model)
        if len(df) == df_len:
            break
    return df


def test_all(A_values, B_values, O_values, Q_values, df, trials, model):
    for a in A_values:
        df_len = len(df)
        df = test_A(a, B_values, O_values, Q_values, df, trials, model)
        if len(df) == df_len:
            break
    return df