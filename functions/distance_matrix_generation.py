import numpy as np
from typing import Callable, Any, Tuple

def dist_i_j_strict_s_shape(i:int, j:int, num_bays:int, between_aisle_dist:float, between_bay_dist:float, big_M:float, **unused:Any) -> int:
    """
    Given two slot indices i and j, calculated the distance from i to j 
    for the strict S-shape policy (note that this is not symmetric due to unidirectionality in the warehouse)    

    Inputs:
    - i: the index of the first slot
    - j: the index of the second slot
    - num_bays: the number of bays per aisle in the warehouse
    - between_aisle_dist: the distance between consecutive aisles in the warehouse
    - between_bay_dist: the distance between consecutive bays in the warehouse
    - big_M: a non-infinite value that forbids backtracking in the warehouse. This allows the distance matrix to be used with a MILP solver (i.e. Gurobi)

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
        return big_M
    elif (aisle_j - aisle_i) % 2 == 0:
        return (aisle_j - aisle_i)*M + 2*L
    elif (aisle_j - aisle_i) % 2 == 1:
        return (aisle_j - aisle_i)*M + L


def build_distance_matrix(pairwise_distance_function:Callable, num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, big_M:float=10000, **unused:Any):
    """
    Calculate the distance matrix for a particular warehouse type given its input parameters

    Inputs:
    - pairwise_distance_function: the function used to calculate pairwise distances between two slots in the warehouse, depending on the warehouse type
    - num_aisle: the number of aisles in the warehouse
    - num_bays: the number of bays per aisle in the warehouse
    - slot_capacity: the capacity of each slot in the warehouse. The standard is 2
    - between_aisle_dist: the distance between consecutive aisles in the warehouse
    - between_bay_dist: the distance between consecutive bays in the warehouse
    - big_M: a non-infinite value that forbids backtracking in the warehouse. This allows the distance matrix to be used with a MILP solver (i.e. Gurobi)

    Outputs:
    - a pairwise distance matrix for the specific warehouse structure
    """
    
    total_slots = num_aisles*num_bays*slot_capacity

    d = np.zeros((total_slots, total_slots))

    for i in range(1, total_slots+1):
        for j in range(1, total_slots+1):
            d[i-1,j-1] = pairwise_distance_function(i, j, num_bays, between_aisle_dist, between_bay_dist, big_M)

    return d


# creating the distance matrix for the transverse warehouse

def build_distance_matrix_transverse(num_aisles:int, num_bays:int, between_aisle_distance:float, between_bay_distance:float, backtrack_penalty:float) -> np.ndarray:
    """
    Calculates the pairwise distances between slots in a warehouse with directional aisles and a single transverse 

    Inputs:
    - num_aisles: the number of aisles in the warehouse
    - num_bays: the number of bays in the warehouse
    - between_aisle_distance: the distance between consecutive aisles in the warehouse
    - between_bay_distance: the distance between consecutive bays in the warehouse
    - penalty: the penalty associated with going the wrong way down directional aisles. This is not set to inf to allow use in Gurobi models

    Outputs:
    - distance_matrix: the matrix of pairwise distances between all slots in the warehouse
    """

    num_slots = num_bays * num_aisles
    M = between_aisle_distance
    N = between_bay_distance

    # initialise the distance matrix
    D = np.zeros((num_slots, num_slots))

    # generate the slots we will work through
    slots = [(x,y) for x in range(1, num_aisles+1) for y in range(1, num_bays+1)]

    # generating the matrix of pairwise distances between slots
    for slot_1 in slots:
        #print(f"slot 1:{slot_1}")
        for slot_2 in slots:
            #print(f"slot 2:{slot_2}")
            aisle_1 = slot_1[0] # calculate the aisles and bays now for use later
            aisle_2 = slot_2[0]
            bay_1 = slot_1[1]
            bay_2 = slot_2[1]
            aisle_diff = aisle_2 - aisle_1
            #print(f"slot 1:{(aisle_1, bay_1)}, slot_2:{aisle_2, bay_2}, slot_2:{slot_2}")

            # if the second slot is further into the warehouse than the first slot
            if aisle_diff > 0.5:
                #print("Entered First Loop")
                # if both slots are in the bottom half
                if bay_1 <= num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 1: # BB, OO
                    #print(f"{slot_1},{slot_2} entered_1")
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff # BB, UU
                elif bay_1 <= num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 0: # BB, OE
                    #print(f"{slot_1},{slot_2} entered_2")
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N + M * aisle_diff # BB, UD
                elif bay_1 <= num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 0: # BB, EE
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff # BB, DD
                    #print(f"{slot_1},{slot_2} entered_3")
                elif bay_1 <= num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 1: # BB, EO
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N + M * aisle_diff # BB, DU
                    #print(f"{slot_1},{slot_2} entered_4")


                # if the first slot is in the bottom half and the second slot is in the top half
                elif bay_1 <= num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 1: # BT, OO
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N + M * aisle_diff # BT, UU
                    #print(f"{slot_1},{slot_2} entered_5")
                elif bay_1 <= num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 0: # BT, OE
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff # BT, UD
                    #print(f"{slot_1},{slot_2} entered_6")
                elif bay_1 <= num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 0: # BT, EE
                    D[slots.index(slot_1), slots.index(slot_2)] = 3*(num_bays/2 + 1)*N + M * aisle_diff # BT, DD
                    #print(f"{slot_1},{slot_2} entered_7")
                elif bay_1 <= num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 1: # BT, EO
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff # BT, DU
                    #print(f"{slot_1},{slot_2} entered_8")


                # if the first slot is in the top half and the second slot is in the bottom half
                elif bay_1 > num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 1: # TB, OO
                    D[slots.index(slot_1), slots.index(slot_2)] = 3*(num_bays/2 + 1)*N + M * aisle_diff # TB, UU
                    #print(f"{slot_1},{slot_2} entered_9")
                elif bay_1 > num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 0: # TB, OE
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff # TB, UD
                    #print(f"{slot_1},{slot_2} entered_10")
                elif bay_1 > num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 0: # TB, EE
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N + M * aisle_diff # TB, DD
                    #print(f"{slot_1},{slot_2} entered_11")
                elif bay_1 > num_bays/2 and bay_2 <= num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 1: # TB, EO
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff # TB, DU
                    #print(f"{slot_1},{slot_2} entered_12")


                # if both slots are in the top half
                elif bay_1 > num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 1: # TT, OO
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff
                    #print(f"{slot_1},{slot_2} entered_13")
                elif bay_1 > num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 1 and aisle_2 % 2 == 0: # TT, OE
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N + M * aisle_diff
                    #print(f"{slot_1},{slot_2} entered_14")
                elif bay_1 > num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 0: # TT, EE
                    D[slots.index(slot_1), slots.index(slot_2)] = 2*(num_bays/2 + 1)*N + M * aisle_diff
                    #print(f"{slot_1},{slot_2} entered_15")   
                elif bay_1 > num_bays/2 and bay_2 > num_bays/2 and aisle_1 % 2 == 0 and aisle_2 % 2 == 1: # TB, EO
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N + M * aisle_diff
                    #print(f"{slot_1},{slot_2} entered_16")

            # if the slots are in the same aisle
            elif aisle_diff == 0:
                #print("Entered second loop")
                #print(f"bay 1:{bay_1}, bay 2:{bay_2}")
                if bay_1 > num_bays/2 and bay_2 > num_bays/2: # both slots are T
                    D[slots.index(slot_1), slots.index(slot_2)] = 0
                    #print("fail to pass 1")
                elif bay_1 <= num_bays/2 and bay_2 <= num_bays/2: # both slots are B
                    D[slots.index(slot_1), slots.index(slot_2)] = 0  
                    #print("fail to pass 2")
                elif aisle_1 % 2 == 1 and bay_1 <= num_bays/2 and bay_2 > num_bays/2: # we are in an up aisle and slot_1 is B and slot_2 is T
                    #print("Entered correct place")
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N
                elif aisle_1 % 2 == 0 and bay_1 > num_bays/2 and bay_2 <= num_bays/2: # we are in a down aisle slot_1 is T and slot_2 is B
                    D[slots.index(slot_1), slots.index(slot_2)] = (num_bays/2 + 1)*N
                else:
                    #print(f"{slot_1}, {slot_2} entered_inf")
                    D[slots.index(slot_1), slots.index(slot_2)] = backtrack_penalty
            else:
                D[slots.index(slot_1), slots.index(slot_2)] = backtrack_penalty

    # generating the distances from the door to each of the slots
    D_row = np.zeros((1,num_slots))

    for slot in slots:
        aisle = slot[0]
        bay = slot[1]
        if bay <= num_bays/2 and aisle % 2 == 1: # B, O
            D_row[0,slots.index(slot)] = (num_bays/2 + 1)*N + (aisle-1)*M # adjust here if wrong

        elif bay > num_bays/2 and aisle % 2 == 1: # T, O
            D_row[0,slots.index(slot)] = 2*(num_bays/2 + 1)*N + (aisle-1)*M

        elif bay <= num_bays/2 and aisle % 2 == 0: # B, E
            D_row[0,slots.index(slot)] = 2*(num_bays/2 + 1)*N + (aisle-1)*M

        elif bay > num_bays/2 and aisle % 2 == 0: # T, E
            D_row[0,slots.index(slot)] = 3*(num_bays/2 + 1)*N + (aisle-1)*M

    # generating the distances from each of the slots to the door
    D_col = np.zeros((num_slots+1,1))

    for slot in slots:
        aisle = slot[0]
        bay = slot[1]
        if bay <= num_bays/2 and aisle % 2 == 1: # B, O
            D_col[slots.index(slot)+1,0] = (num_bays/2 + 1)*N + M*max(aisle-1, 2)

        elif bay > num_bays/2 and aisle % 2 == 1: # T, O
            D_col[slots.index(slot)+1,0] = 2*(num_bays/2 + 1)*N + M*max(aisle-1, 2)

        elif bay <= num_bays/2 and aisle % 2 == 0: # B, E
            D_col[slots.index(slot)+1,0] = (aisle-1)*M

        elif bay > num_bays/2 and aisle % 2 == 0: # T, E
            D_col[slots.index(slot)+1,0] = (num_bays/2 + 1)*N + (aisle-1)*M

    # creating the full pairwise distance matrix, including the door
    D_tall = np.vstack((D_row, D))
    D_full = np.hstack((D_col, D_tall))

    return D_full


def build_pairwise_product_distance_matrix(slot_assignments_dict:dict[int,Tuple[int,int]], slots:list[Tuple[int,int]], num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, backtrack_penalty:int) -> np.ndarray:
    """
    Takes the matrix for the pairwise distances between slots in the warehouse and the product assignments to create a new distance matrix for the pairwise distances between products

    Inputs:
    - slot_assignments_dict: the assignments of products to slots
    - num_aisles: the number of aisles in the warehouse
    - num_bays: the number of bays in the warehouse
    - slot_capacity: the capacity of a single slot in the warehouse. The standard is two
    - between_aisle_dist: the distance between consecutive aisles in the warehouse
    - between_bay_dist: the distance between two consecutive bays in the warehouse
    - penalty: the penalty enforcing aisle directionality

    Outputs:
    - distance_matrix: the matrix of pairwise distances between products in the warehouse
    """

    between_slot_distance_matrix = build_distance_matrix_transverse(num_aisles, num_bays, between_aisle_dist, between_bay_dist, backtrack_penalty)
    num_slots = num_aisles * num_bays
    num_products = num_slots * slot_capacity
    between_prod_distance_matrix = np.zeros((num_products+1, num_products+1))
    
    # between pairs of products
    for prod_1 in range(1, num_products+1):
        for prod_2 in range(1, num_products+1):
            slot_1 = slot_assignments_dict[prod_1] # extracts the tuple associated with the slot to which the product is assigned
            slot_2 = slot_assignments_dict[prod_2]
            distance = between_slot_distance_matrix[slots.index(slot_1)+1, slots.index(slot_2)+1] # extract the distance between the two slots to whih the products are assigned
            between_prod_distance_matrix[prod_1,prod_2] = distance # this is equal to the distance between the two products

    # from door to product
    for prod in range(1, num_products+1):
        slot = slot_assignments_dict[prod]
        distance = between_slot_distance_matrix[0,slots.index(slot)+1]
        between_prod_distance_matrix[0,prod] = distance

    # from product to door
    for prod in range(1, num_products+1):
        slot = slot_assignments_dict[prod]
        distance = between_slot_distance_matrix[slots.index(slot)+1,0]
        between_prod_distance_matrix[prod,0] = distance

    return between_prod_distance_matrix