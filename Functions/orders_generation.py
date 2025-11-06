
import random

def generate_orders(num_orders:int, order_size:int, num_products:int) -> dict:

    Orders = {}
    count = 1

    for order in range(num_orders):
        order = []
        prod_list = [y for y in range(1, num_products + 1)]
        order = random.sample(prod_list, order_size)
        Orders[count] = order
        count += 1

    return Orders