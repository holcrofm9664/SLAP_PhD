from functions.full_optimisation_model import full_optimisation_model
from functions.instance_generation import generate_instances
import pandas as pd

A = [1, 3]
B = [2, 4, 6]
O = [1, 3]
Q = [3, 5]
slot_capacity = 2
between_aisle_dist = 1
between_bay_dist = 1
seed = 123

product_df = {
    "prod_id": [
        1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
        25,26,27,28,29,30,31,32,33,34,35,36
    ],
    "weight": [
        6.3, 1.8, 9.4, 0.2, 7.1, 3.6, 5.9, 8.0, 2.7, 4.1, 6.8, 0.5,
        9.9, 1.2, 7.4, 3.0, 8.6, 4.7, 5.1, 2.3, 6.0, 0.9, 7.8, 1.6,
        4.9, 2.1, 8.3, 6.5, 0.7, 9.1, 3.8, 5.6, 1.4, 7.0, 2.9, 6.2
    ],
    "cluster": [
        3, 1, 4, 2, 2, 3, 1, 4, 3, 2, 1, 4,
        2, 3, 4, 1, 2, 3, 1, 4, 2, 3, 4, 1,
        3, 2, 4, 1, 3, 2, 4, 1, 2, 3, 1, 4
    ]
}

crushing_multiple = 2
backtrack_penalty = 1000
time_limit = 3600

# generate the instances
combinations = generate_instances(A = A, B = B, O = O, Q = Q, slot_capacity = slot_capacity, between_aisle_dist = between_aisle_dist, between_bay_dist = between_bay_dist, seed = seed, product_df = product_df, crushing_multiple = crushing_multiple, backtrack_penalty = backtrack_penalty, time_limit = time_limit)
# for each instance, run the full model
assignments_list = []
distance_1_list = []
distance_2_list = []
runtime_stage_1_list = []
runtime_stage_2_list = []
runtime_total_list = []

for combination in combinations:
    assignments, distance_1, distance_2, runtime_stage_1, runtime_stage_2, runtime_total = full_optimisation_model(**combination)
    assignments_list.append(assignments)
    distance_1_list.append(distance_1)
    distance_2_list.append(distance_2)
    runtime_stage_1_list.append(runtime_stage_1)
    runtime_stage_2_list.append(runtime_stage_2)
    runtime_total_list.append(runtime_total)

# add the results from each instance to a dictionary
results_dict = {}

results_dict["assignments"] = assignments_list
results_dict["distance_without_transverse"] = distance_1_list
results_dict["distance_with_transverse"] = distance_2_list
results_dict["first_optimisation_runtime"] = runtime_stage_1_list
results_dict["second_optimisation_runtime"] = runtime_stage_2_list
results_dict["total_optimisation_runtime"] = runtime_total_list

# make the dictionary into a dataframe
results_df = pd.DataFrame(results_dict)

print(results_df)
# save the dataframe to a .csv file

results_df.to_csv("output/full_optimisation_model_results.csv")