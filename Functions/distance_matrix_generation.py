import numpy as np

def calculate_aisle(i, num_bays):
    return np.ceil(i/num_bays)


def dist_i_j_strict_s_shape(i, j, M, N, num_bays):
    aisle_i = calculate_aisle(i, num_bays)
    aisle_j = calculate_aisle(j, num_bays)
    L = N*(num_bays+1)
    if aisle_i == aisle_j:
        return 0
    elif aisle_i > aisle_j:
        return np.inf
    elif (aisle_j - aisle_i) % 2 == 0:
        return (aisle_j - aisle_i)*M + 2*L
    elif (aisle_j - aisle_i) %2 == 1:
        return (aisle_j - aisle_i)*M + L