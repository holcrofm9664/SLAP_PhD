import numpy as np
from typing import Callable, Any

def dist_i_j_strict_s_shape(i:int, j:int, num_bays:int, between_aisle_dist:float, between_bay_dist:float, **unused:Any) -> int:
    """
    Given two slot indices i and j, calculated the distance from i to j 
    for the strict S-shape policy (note that this is not symmetric due to unidirectionality in the warehouse)    

    Inputs:
    - i: the index of the first slot
    - j: the index of the second slot
    - num_bays: the number of bays per aisle in the warehouse
    - between_aisle_dist: the distance between consecutive aisles in the warehouse
    - between_bay_dist: the distance between consecutive bays in the warehouse

    Outputs:
    - the distance between the two bays
    """

    M = between_aisle_dist
    N = between_bay_dist

    aisle_i = np.ceil(i/num_bays)
    aisle_j = np.ceil(j/num_bays)
    L = N*(num_bays+1)
    if aisle_i == aisle_j:
        return 0
    elif aisle_i > aisle_j:
        return np.inf
    elif (aisle_j - aisle_i) % 2 == 0:
        return (aisle_j - aisle_i)*M + 2*L
    elif (aisle_j - aisle_i) % 2 == 1:
        return (aisle_j - aisle_i)*M + L


def build_distance_matrix(pairwise_distance_function:Callable, num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, **unused:Any):
    """
    Calculate the distance matrix for a particular warehouse type given its input parameters

    Inputs:
    - pairwise_distance_function: the function used to calculate pairwise distances between two slots in the warehouse, depending on the warehouse type
    - num_aisle: the number of aisles in the warehouse
    - num_bays: the number of bays per aisle in the warehouse
    - slot_capacity: the capacity of each slot in the warehouse. The standard is 2
    - between_aisle_dist: the distance between consecutive aisles in the warehouse
    - between_bay_dist: the distance between consecutive bays in the warehouse
    
    """
    
    total_slots = num_aisles*num_bays*slot_capacity

    d = np.zeros((total_slots, total_slots))

    for i in range(1, total_slots+1):
        for j in range(1, total_slots+1):
            d[i-1,j-1] = pairwise_distance_function(i, j, num_bays, between_aisle_dist, between_bay_dist)

    return d
