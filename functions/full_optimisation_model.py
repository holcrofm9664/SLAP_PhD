from functions.distance_matrix_generation import build_pairwise_product_distance_matrix
from models.full_models.strict_s_shape import Strict_S_Shape
from models.sub_models.weight_fragility import weight_fragility
from functions.tsp import total_distance_for_all_orders
import numpy as np

def full_optimisation_model(product_df, orders, num_aisles, num_bays, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, cluster_max_distance, backtrack_penalty, time_limit):
    
    # ensure that an even number of bays is entered (such that the aisle may be split in half to include the transverse)
    if num_bays % 2 != 0:
        print("The warehouse must have an even number of bays")
        return "NA", "NA", "NA"

    # get the number of products and the slot (aisle, bay) tuple pairs
    num_prods = num_aisles*num_bays*slot_capacity
    slots = [(x,y) for x in range(1,num_aisles+1) for y in range(1, num_bays+1)]
    
    # extract the product clusters and weights from the product attributes dataframe
    cluster_assignments = list(product_df["cluster"])
    weights = list(product_df["weight"])

    # create the crushing array based on product weights
    crushing_array = np.zeros((num_prods, num_prods))

    for prod_1 in range(num_prods):
        for prod_2 in range(num_prods):
            if weights[prod_2] >= crushing_multiple*weights[prod_1]: # for now, one product is assumed able to crush another if it weighs twice as much
                crushing_array[prod_1, prod_2] = 1

    # run the strict s-shape model to assign products to aisles, as though the warehouse was directional and had no transverse aisle
    status, distance_no_transverse, runtime_first_stage, aisle_assignments_dict = Strict_S_Shape(num_aisles = num_aisles, num_bays = num_bays, slot_capacity = slot_capacity, between_aisle_dist=between_aisle_dist, between_bay_dist=between_bay_dist, orders = orders, time_limit=time_limit)

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
        _, _, _, _, slot_assignments_dict = weight_fragility(prods_in_aisle, orders=orders_new, crushing_array=crushing_array, cluster_assignments=cluster_assignments, num_bays=num_bays, slot_capacity=slot_capacity, cluster_max_distance=cluster_max_distance, slot_assignments_dict = slot_assignments_dict, output_flag=False, aisle=aisle)

    # calculate the pairwise product distance matrix assuming now that the warehouse has a transverse bisecting aisles

    between_product_distance_matrix = build_pairwise_product_distance_matrix(slot_assignments_dict, slots, 2, 4, 2, 1, 1, 100)

    distance_transverse, per_order = total_distance_for_all_orders(orders, between_product_distance_matrix=between_product_distance_matrix)

    return f"Assignments: {slot_assignments_dict}", f"Distance with no transverse: {distance_no_transverse}", f"Distance including the transverse: {distance_transverse}"