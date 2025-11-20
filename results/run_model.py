from functions.results import solve_all
from itertools import product
import pickle


A_vals = [1,3,5,10]
B_vals = [5,10]
O_vals = [1,3,5,10]
Q_vals = [5,10]
slot_capacity = 2
between_aisle_dist = 1
between_bay_dist = 1
num_trials = 2

instances = product(A_vals, B_vals, Q_vals, O_vals)

instance = {"instances":instances,
            "slot_capacity":slot_capacity,
            "between_aisle_dist":between_aisle_dist,
            "between_bay_dist":between_bay_dist,
            "num_trials":num_trials}


df, orders_dict = solve_all(**instance)

with open("output/orders_dict.pkl","wb") as f:
    pickle.dump(orders_dict, f)

df.to_csv("output/results.csv")

