from functions.orders_generation import generate_orders
import pandas as pd

def generate_instances_parallelisation(A:list, B:list, O:list, Q:list, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, seed:int, product_df:pd.DataFrame, crushing_multiple:float, backtrack_penalty:int, time_limit:int) -> list[tuple]:
    """
    Generates all possible combinations of inputs given the user inputs which parameter values they would like to test

    Inputs:
    - A: a list containing the different aisle numbers that will be tested
    - B: a list containing the different bay numbers that will be tested
    - O: a list containing the different numbers of orders that will be tested
    - Q: a list containing the different order sizes that will be tested
    - slot_capacity: the capacity of slots in the warehouse. The standard is 2
    - between_aisle_dist: the distance between two consecutive aisles
    - between_bay_distance: the distance between two consecutive bays
    - seed: the seed used in generating the orders
    - product_df: a pandas dataframe containing the product ids and attributes such as weight and cluster
    - crushing_multiple: the amount by which one product has to be heavier than another to crush it, as a multiple of the lighter product
    - backtrack_penalty: the penalty applied for going against the one-way system
    - time_limit: the time limit set for the assignment of products to aisles

    Outputs:
    - combinations: a list of dictionaries, where each dictionary constitutes an instance
    """
    
    combinations = []

    for a in A:
        for b in B:
            num_products = a * b * slot_capacity
            for o in O:
                for q in Q:
                    if num_products >= q: # ensures that combinations are only generated for instances for which there are enough products to fill a single order
                        orders = generate_orders(num_orders = o, order_size = q, num_products = num_products, seed=seed)

                        cluster_max_dist = b/2

                        instance = (product_df, orders, a, b, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, cluster_max_dist, backtrack_penalty, time_limit)

                        combinations.append(instance)
    
    return combinations
    





def generate_instances_kwargs(A:list, B:list, O:list, Q:list, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, seed:int, product_df:pd.DataFrame, crushing_multiple:float, backtrack_penalty:int, time_limit:int) -> list[dict]:
    """
    Generates all possible combinations of inputs given the user inputs which parameter values they would like to test

    Inputs:
    - A: a list containing the different aisle numbers that will be tested
    - B: a list containing the different bay numbers that will be tested
    - O: a list containing the different numbers of orders that will be tested
    - Q: a list containing the different order sizes that will be tested
    - slot_capacity: the capacity of slots in the warehouse. The standard is 2
    - between_aisle_dist: the distance between two consecutive aisles
    - between_bay_distance: the distance between two consecutive bays
    - seed: the seed used in generating the orders
    - product_df: a pandas dataframe containing the product ids and attributes such as weight and cluster
    - crushing_multiple: the amount by which one product has to be heavier than another to crush it, as a multiple of the lighter product
    - backtrack_penalty: the penalty applied for going against the one-way system
    - time_limit: the time limit set for the assignment of products to aisles

    Outputs:
    - combinations: a list of dictionaries, where each dictionary constitutes an instance
    """
    
    combinations = []

    for a in A:
        for b in B:
            num_products = a * b * slot_capacity
            for o in O:
                for q in Q:
                    if num_products >= q: # ensures that combinations are only generated for instances for which there are enough products to fill a single order
                        orders = generate_orders(num_orders = o, order_size = q, num_products = num_products, seed=seed)

                        
                        instance = {}
                        instance["num_aisles"] = a
                        instance["num_bays"] = b
                        instance["slot_capacity"] = slot_capacity
                        instance["between_aisle_dist"] = between_aisle_dist
                        instance["between_bay_dist"] = between_bay_dist
                        instance["orders"] = orders
                        instance["product_df"] = product_df
                        instance["crushing_multiple"] = crushing_multiple
                        instance["cluster_max_dist"] = b/2
                        instance["backtrack_penalty"] = backtrack_penalty
                        instance["time_limit"] = time_limit

                        combinations.append(instance)
    
    return combinations





def generate_single_instance(num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, orders:dict) -> dict:
    """
    Generates a single instance given all the relevant inputs
    
    Inputs:
    - num_aisles: the number of aisles in the warehouse
    - num_bays: the number of bays in the warehouse
    - slot_capacity: the capacity of slots in the warehouse. The standard is two (one either side of the aisle)
    - between_aisle_dist: the distance between consecutive aisles
    - between_bay_dist: the distance between consecutive bays
    - orders: the dictionary of orders
    
    Output:
    - instance: the instance, given in the form of a dictionary (for easy use with kwargs)
    """
    
    instance = {}
    instance["num_aisles"] = num_aisles
    instance["num_bays"] = num_bays
    instance["slot_capacity"] = slot_capacity
    instance["between_aisle_dist"] = between_aisle_dist
    instance["between_bay_dist"] = between_bay_dist
    instance["orders"] = orders

    return instance