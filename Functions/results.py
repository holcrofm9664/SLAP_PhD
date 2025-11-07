import pandas as pd
from Functions.orders_generation import generate_orders
from Functions.instance_generation import generate_single_instance

def test_model(model, A, B, O, Q, num_trials, C):
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
                        num_prods = a * b * C
                        orders = generate_orders(o, q, num_prods)
                        instance = generate_single_instance(a, b, C, 1, 1, orders)
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