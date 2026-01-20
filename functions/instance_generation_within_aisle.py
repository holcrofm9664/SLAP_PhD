from functions.orders_generation import generate_orders
import numpy as np
import random
from collections import Counter

def generate_instance_WASAP(num_bays:int, slot_capacity:int, num_orders:int, order_size:int, cluster_max_distance:int, num_clusters:int, seed:int) -> dict[dict[int,list[int]], np.ndarray[int], list[int], int, int, int]:
    """
    Creates a single instance on which the within-aisle storage assignment model may be run

    Inputs:
    - num_bays: the number of bays the aisle is divided into
    - slot_capacity: the capacity of each bay
    - num_orders: the number of orders we wish to generate
    - order_size: the size of the orders we wish to generate
    - cluster_max_distance: the maximum distance two products within the same cluster may be placed apart from each other
    - num_clusters: the number of clusters into which we wish to divide products
    - seed: the seed used in orders generation
    
    Outputs:
    - a dictionary containing all of the required inputs for the within-aisle assignment model
    """
    
    num_products = slot_capacity * num_bays

    orders = generate_orders(num_orders = num_orders, order_size = order_size, num_products = num_products, seed = seed)

    crushing_array = np.zeros((num_products, num_products))

    for i in range(num_products):
        for j in range(num_products):
            crushing_array[i,j] = random.randint(0,1)

    np.fill_diagonal(crushing_array, 0)

    cluster_assignments = []

    for i in range(num_products):
        cluster = random.randint(1, num_clusters)
        cluster_assignments.append(cluster)

    max_size = max(Counter(cluster_assignments).values())

    cluster_max_distance = max_size/2 ## this is arbitrary

    instance = {"orders":orders,
                "crushing_array":crushing_array,
                "cluster_assignments":cluster_assignments,
                "num_bays":num_bays,
                "slot_capacity":slot_capacity,
                "cluster_max_distance":cluster_max_distance
                }
    
    return instance