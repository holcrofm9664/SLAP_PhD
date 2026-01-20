from functions.distance_matrix_generation import build_pairwise_product_distance_matrix
from functions.tsp import total_distance_for_all_orders
import random

def transverse_distance_using_fixed_aisle_assignments(orders:dict[int,list[int]], num_aisles:int, num_bays:int, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float, aisle_assignments:dict[int,int], backtrack_penalty:int) -> float:
    """
    A function which takes in the fixed aisle assignments calculated by the Strict S-Shape model and calculates what the distance would be should the warehouse 
    have the option of using a transverse when routing.

    Inputs:
    - orders: the orders used to obtain the aisle assignments
    - num_aisles: the number of aisles in the warehouse
    - num_bays: the number of bays in the warehouse
    - slot_capacity: the capacity of a slot in the warehouse
    - between_aisle_dist: the distance between consecutive aisles within the warehouse
    - between_bay_distance: the distance between consecutive bays in the warehouse
    - aisle_assignments: the assignments of products to aisles from the Strict S-Shape model
    - backtrack_penalty: the penalty to be used in the pairwise slot distance matrix to enforce aisle directionality

    Outputs:
    - distance_transverse: the total distance if a transverse may be used to route between slots
    """

    def aisle_to_slot_assignments(aisle_assignments, num_bays, num_aisles, capacity):
        aisle_vals = {} # the slot numbers for each aisle

        for aisle_num in range(1, num_aisles + 1):
            slot_numbers = [x for x in range((aisle_num-1)*num_bays + 1, aisle_num*num_bays+1)]
            aisle_vals[aisle_num] = slot_numbers * capacity


        slot_assignments = {}

        for prod in aisle_assignments:
            aisle = aisle_assignments[prod]
            values = aisle_vals[aisle]
            slot = random.sample(values, 1)
            slot_assignments[prod] = slot[0]
            values.remove(slot[0])
            aisle_vals[aisle] = values

        return slot_assignments

    slot_assignments = aisle_to_slot_assignments(aisle_assignments,num_bays, num_aisles, slot_capacity)

    M = build_pairwise_product_distance_matrix(slot_assignments, num_aisles, num_bays, slot_capacity, between_aisle_dist, between_bay_dist, backtrack_penalty)

    distance_transverse, per_order_transverse = total_distance_for_all_orders(orders, M)

    return distance_transverse