from functions.distance_matrix_generation import build_pairwise_product_distance_matrix
from models.full_models.strict_s_shape import Strict_S_Shape
from models.sub_models.weight_fragility import weight_fragility
from functions.tsp import total_distance_for_all_orders
import numpy as np
import pandas as pd
from typing import Tuple
import time


DATA_DF = None
ORDERS_LIST = None

def init_worker(data_df, orders_dict_list):
    global DATA_DF, ORDERS_LIST
    DATA_DF = data_df
    ORDERS_LIST = orders_dict_list



def full_optimisation_model(order_idx:int, num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, crushing_multiple:float, cluster_max_dist:int, backtrack_penalty:float, time_limit:float) -> Tuple[dict[int:tuple[int,int]], float, float]:
    """
    A function which takes in the product attributes, orders, and warehouse dimensions, and runs the full optimisation model to assign products to individual slots and calculate the distance for both the warehouse with the transverse and without

    Inputs:
    - product_df: a pandas dataframe containing product attributes, including their id, weight and cluster (which could be interpreted as aisle/zone in destination store)
    - orders: a dictionary of orders
    - num_aisles: the number of aisles in the warehouse
    - num_bays: the number of bays each aisle is divided into
    - slot_capacity: the number of products able to be assigned to each (aisle,bay) pair. The standard is 2
    - between_aisle_dist: the distance between two consecutive aisles
    - between_bay_dist: the distance between two consecutive bays
    - crushing_multiple: how much heavier (in multiples of the lighter product's weight) a heavier product needs to be to crush it. Used to make the crushing array
    - cluster_max_dist: the maximum distance apart two products within the same cluster two products can be placed within one aisle
    - backtrack_penalty: the penalty for backtracking against a one-way system 
    - time_limit: the time allocated for the assignment of products to aisles

    Outputs:
    - slot_assignments_dict: the dictionary containing the assignments of products to slots
    - distance_no_transverse: the distance found after assigning products to aisles, assuming that the warehouse does not contain a transverse
    - distance_transverse: the distabce found after assigning products to specific slots and assuming a transverse aisle exists
    """

    orders = ORDERS_LIST[order_idx] # take the correct order set from the globally defined list of orders dictionaries
    product_df = DATA_DF # take the product df from the globally defined variable

    num_orders = len(orders)
    order_size = len(orders[1])

    start_full = time.perf_counter()

    # ensure that an even number of bays is entered (such that the aisle may be split in half to include the transverse)
    if num_bays % 2 != 0:
        print("The warehouse must have an even number of bays")
        return "NA", "NA", "NA"

    # get the number of products and the slot (aisle, bay) tuple pairs
    num_prods = num_aisles*num_bays*slot_capacity
    slots = [(x,y) for x in range(1,num_aisles+1) for y in range(1, num_bays+1)]
    
    # extract the product clusters and weights from the product attributes dataframe
    cluster_assignments = list(product_df["prod_cluster"])
    weights = list(product_df["prod_weight"])

    # create the crushing array based on product weights
    crushing_array = np.zeros((num_prods, num_prods))

    for prod_1 in range(num_prods):
        for prod_2 in range(num_prods):
            if weights[prod_2] >= crushing_multiple*weights[prod_1]: # for now, one product is assumed able to crush another if it weighs twice as much
                crushing_array[prod_1, prod_2] = 1

    # run the strict s-shape model to assign products to aisles, as though the warehouse was directional and had no transverse aisle
    status, distance_no_transverse, runtime_first_stage, aisle_assignments_dict = Strict_S_Shape(num_aisles = num_aisles, num_bays = num_bays, slot_capacity = slot_capacity, between_aisle_dist=between_aisle_dist, between_bay_dist=between_bay_dist, orders = orders, time_limit=time_limit)

    start = time.perf_counter()

    # initialise the slot assignments dictionary
    slot_assignments_dict = {}

    for aisle in range(1, num_aisles+1): # run the within-aisle optimisation model for each aisle
        orders_new = orders.copy() # copy the set of orders
        prods_in_aisle = aisle_assignments_dict[aisle] # extract the products stored in the aisle
        for order in orders_new: # remove products not in the aisle from orders
            prods = orders_new[order]
            prods_new = [x for x in prods if x in prods_in_aisle]
            orders_new[order] = prods_new
        # delete empty orders
        orders_new = {k:v for k,v in orders_new.items() if v}

        # run the within-aisle optimisation model and update the slot assignments dictionary
        _, _, _, slot_assignments_dict = weight_fragility(prods_in_aisle, orders=orders_new, crushing_array=crushing_array, cluster_assignments=cluster_assignments, num_bays=num_bays, slot_capacity=slot_capacity, cluster_max_distance=cluster_max_dist, slot_assignments_dict = slot_assignments_dict, output_flag=False, aisle=aisle)

    end = time.perf_counter()

    # calculate the pairwise product distance matrix assuming now that the warehouse has a transverse bisecting aisles

    between_product_distance_matrix = build_pairwise_product_distance_matrix(slot_assignments_dict = slot_assignments_dict, slots = slots, num_aisles=num_aisles, num_bays=num_bays, slot_capacity=slot_capacity, between_aisle_dist=between_aisle_dist, between_bay_dist=between_bay_dist, backtrack_penalty=backtrack_penalty)

    distance_transverse, per_order = total_distance_for_all_orders(orders, between_product_distance_matrix=between_product_distance_matrix)

    end_full = time.perf_counter()

    runtime_second_stage = end - start
    runtime_total = end_full - start_full

    returns_dict = {"slot_assignments_dict":slot_assignments_dict,
                    "distance_no_transverse":distance_no_transverse,
                    "distance_transverse":distance_transverse,
                    "runtime_first_stage":runtime_first_stage,
                    "runtime_second_stage":runtime_second_stage,
                    "runtime_total":runtime_total,
                    "num_aisles":num_aisles,
                    "num_bays":num_bays,
                    "num_orders":num_orders,
                    "order_size":order_size
    }

    return returns_dict