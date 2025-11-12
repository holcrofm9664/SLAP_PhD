import numpy as np

def calculate_aisle(i, num_bays):
    return np.ceil(i/num_bays)


def dist_i_j_strict_s_shape(i, j, **kwargs):
    num_bays = kwargs["num_bays"]
    M = kwargs["between_aisle_dist"]
    N = kwargs["between_bay_dist"]

    aisle_i = calculate_aisle(i, num_bays)
    aisle_j = calculate_aisle(j, num_bays)
    L = N*(num_bays+1)
    if aisle_i == aisle_j:
        return 0
    elif aisle_i > aisle_j:
        return np.inf
    elif (aisle_j - aisle_i) % 2 == 0:
        return (aisle_j - aisle_i)*M + 2*L
    elif (aisle_j - aisle_i) % 2 == 1:
        return (aisle_j - aisle_i)*M + L


def build_distance_matrix(pairwise_distance_function, **kwargs):
    num_aisles = kwargs["num_aisles"]
    num_bays = kwargs["num_bays"]
    slot_capacity = kwargs["slot_capacity"]
    M = kwargs["between_aisle_dist"]
    N = kwargs["between_bay_dist"]

    total_slots = num_aisles*num_bays*slot_capacity

    d = np.zeros((num_aisles, num_bays))

    for i in range(total_slots):
        for j in range(total_slots):
            d[i,j] = pairwise_distance_function(i, j, **kwargs)

    return d
