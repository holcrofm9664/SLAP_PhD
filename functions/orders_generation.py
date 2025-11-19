import random
from typing import Any

def generate_orders(num_orders:int, order_size:int, num_products:int, seed:int, **unused:Any) -> dict:
    """
    A function to generate orders using random sampling without replacement

    Inputs:
    - num_orders: the number of orders in the specific instance
    - order_size: the size of orders in the specific instance. Note that, for this function, all orders must be of the same size
    - num_products: the total number of products in the warehouse. This is generally taken to be equal to the number of slots in the warehouse

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