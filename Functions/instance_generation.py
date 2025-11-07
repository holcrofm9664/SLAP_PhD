from Functions.orders_generation import generate_orders

def generate_instances(A:list, B:list, O:list, Q:list, slot_capacity:int, between_aisle_dist:float, between_bay_dist:float):

    combinations = []

    for a in A:
        for b in B:
            num_products = a * b * slot_capacity
            for o in O:
                for q in Q:
                    orders = generate_orders(o, q, num_products)
                    instance = {}
                    instance["num_aisles"] = a
                    instance["num_bays"] = b
                    instance["slot_capacity"] = slot_capacity
                    instance["between_aisle_dist"] = between_aisle_dist
                    instance["between_bay_dist"] = between_bay_dist
                    instance["orders"] = orders
                    combinations.append(instance)
    
    return combinations
    

    
def generate_single_instance(num_aisles, num_bays, slot_capacity, between_aisle_dist, between_bay_dist, orders):
    instance = {}
    instance["num_aisles"] = num_aisles
    instance["num_bays"] = num_bays
    instance["slot_capacity"] = slot_capacity
    instance["between_aisle_dist"] = between_aisle_dist
    instance["between_bay_dist"] = between_bay_dist
    instance["orders"] = orders

    return instance