from functions.instance_generation import generate_instances_parallelisation
from functions.orders_generation import generate_orders
from multiprocessing import Pool
import os
import sys
from itertools import product
import pandas as pd
from results.worker import init_worker, full_optimisation_model
import json




def build_tasks(A, B, O, Q, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, backtrack_penalty, time_limit, seed):
    for num_orders, order_size, num_aisles, num_bays in product(O, Q, A, B):

        num_products = num_aisles * num_bays * 2

        if num_products < order_size:
            continue

        
        orders = generate_orders(num_orders, order_size, num_products, seed)

        cluster_max_dist = num_bays/2

        yield (
            orders,
            num_aisles,
            num_bays,
            slot_capacity,
            between_aisle_dist,
            between_bay_dist, 
            crushing_multiple,
            cluster_max_dist,
            backtrack_penalty,
            time_limit,
        )



def run(product_df, A, B, O, Q, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, backtrack_penalty, time_limit, chunksize, seed):
    
    tasks = build_tasks(A = A,
                        B = B,
                        O = O,
                        Q = Q,
                        slot_capacity = slot_capacity,
                        between_aisle_dist = between_aisle_dist,
                        between_bay_dist = between_bay_dist,
                        crushing_multiple = crushing_multiple,
                        backtrack_penalty = backtrack_penalty,
                        time_limit = time_limit,
                        seed = seed
                        )
    
    #num_workers = os.environ.get("SLURM_CPUS_PER_TASK", os.cpu_count() or 1)
    num_workers = int(sys.argv[1])

    with Pool(
        processes=num_workers,
        initializer=init_worker,
        initargs=(product_df,),
    ) as p:
        rows = p.starmap(full_optimisation_model, tasks, chunksize=chunksize)

    df = pd.DataFrame(rows)

    return df


def main(A, B, O, Q, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, backtrack_penalty, time_limit, chunksize, seed):
    product_df = pd.read_parquet("data/prod_df.parquet")

    df = run(product_df = product_df,
             A = A,
             B = B,
             O = O,
             Q = Q,
             slot_capacity = slot_capacity,
             between_aisle_dist = between_aisle_dist,
             between_bay_dist = between_bay_dist,
             crushing_multiple = crushing_multiple,
             backtrack_penalty=backtrack_penalty,
             time_limit=time_limit,
             chunksize=chunksize,
             seed = seed)
    
    def slot_dict_to_json(d):
        if isinstance(d, dict):
            return json.dumps({str(k):list(v) for k, v in d.items()})
        return None
    
    df["slot_assignments_dict"] = df["slot_assignments_dict"].apply(slot_dict_to_json)

    df.to_parquet("data/test_output.parquet", index = False)  # error here

    return df


if __name__ == "__main__":
    main(
        A = [1,3,5],
        B = [2,4,6],
        O = [1,3,5],
        Q = [3,5,10],
        slot_capacity = 2,
        between_aisle_dist=1,
        between_bay_dist=1, 
        crushing_multiple=2,
        backtrack_penalty=1000,
        time_limit=3600,
        chunksize=50,
        seed = 123
    )

