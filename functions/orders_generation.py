import random
from typing import Any

def generate_orders(num_orders:int, order_size:int, num_products:int, seed:int, **unused:Any) -> dict[int:list[int]]:
    """
    A function to generate orders using random sampling without replacement

    Inputs:
    - num_orders: the number of orders in the specific instance
    - order_size: the size of orders in the specific instance. Note that, for this function, all orders must be of the same size
    - num_products: the total number of products in the warehouse. This is generally taken to be equal to the number of slots in the warehouse
    - seed: the seed used to generate the random numbers

    Output:
    - Orders: a dictionary of orders for one instance
    """
    
    Orders = {}
    count = 1

    random.seed(seed)

    for order in range(num_orders):
        order = []
        prod_list = list(range(1, num_products + 1))
        order = random.sample(prod_list, order_size)
        Orders[count] = order
        count += 1

    return Orders


def reduce_orders(orders:dict[int:list[int]], aisle:int, aisle_assignments_dict:dict[int:list[int]]):
    """
    Takes the full dictionary of orders arriving in the warehouse and the aisle we are optimising, and removes all but the products stored on the aisle (and deletes empty orders)

    Inputs:
    - orders: the dictionary of all orders being used in the full warehouse optimisation
    - aisle: the aisle we are optimising
    - aisle_assignments_dict: the dictionary containing the aisles as keys and products assigned to each aisle stored as integers in a list as the values

    Output: 
    - The reduced orders, including now only products assigned to that aisle
    - The products assigned to the aisle
    """

    orders_new = orders.copy()
    prods_in_aisle = aisle_assignments_dict[aisle]
    for order in orders_new: # remove products not in the aisle from orders
        prods = orders_new[order]
        prods_new = [x for x in prods if x in prods_in_aisle]
        orders_new[order] = prods_new
    # delete empty orders
    orders_new = {k:v for k,v in orders_new.items() if v}

    return orders_new, prods_in_aisle