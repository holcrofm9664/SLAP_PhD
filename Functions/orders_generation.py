
import random

def generate_orders(num_orders:int, order_size:int, num_products:int) -> dict:

    Orders = {}
    count = 1

    for order in range(num_orders):
        order = []
        prod_list = [y for y in range(1, num_products + 1)]
        while len(order) < order_size:
            idx = random.randint(0, len(prod_list) - 1)
            order.append(prod_list[idx])
            prod_list.pop(idx)
        Orders[count] = order
        count += 1

    return Orders