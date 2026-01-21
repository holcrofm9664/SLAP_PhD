import numpy as np

def generate_crushing_array(num_prods:int, weights:list[float], crushing_multiple:float) -> np.ndarray[int]:
    """
    Creates a 0-1 array, array[prod_1, prod_2] == 0 implies prod_1 cannot crush prod_2, and array[prod_1,prod_2] == 1 implies prod_1 can crush prod_2
    
    Inputs:
    - num_prods: the number of products in the warehouse, taken as num_aisles*num_bays*slot_capacity
    - weights: a list containing the weights of each of the products
    - crushing_multiple: how much heavier, as a multiple of the lighter product, does the heavier product have to be to crush it

    Outputs:
    - an array containing all 0 and 1 values, where 0 implies that product 2 cannot crush product 1, and 1 implies that product 2 can crush product 1
    """

    # create the crushing array based on product weights
    crushing_array = np.zeros((num_prods, num_prods))

    for prod_1 in range(num_prods):
        for prod_2 in range(num_prods):
            if weights[prod_2] >= crushing_multiple*weights[prod_1]:
                crushing_array[prod_1, prod_2] = 1

    return crushing_array