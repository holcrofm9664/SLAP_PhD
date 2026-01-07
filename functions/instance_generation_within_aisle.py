from functions.orders_generation import generate_orders
import numpy as np
import random
from collections import Counter

def generate_instance_WASAP(num_bays, slot_capacity, num_orders, order_size, cluster_max_distance, num_clusters, seed):

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