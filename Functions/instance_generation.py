from Functions.Orders_Generation import generate_orders

def generate_instances(A:list, B:list, O:list, Q:list, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float):

    combinations = {}
    count = 1

    for a in A:
        for b in B:
            num_products = a * b * slot_capacity
            for o in O:
                for q in Q:
                    orders = generate_orders(o, q, num_products)
                    combinations[count] = [a, b, slot_capacity, between_aisle_dist, between_bay_dist, orders]
                    count += 1
    
    return combinations
    
    