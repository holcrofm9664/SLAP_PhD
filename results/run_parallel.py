from functions.instance_generation import generate_instances_parallelisation
from functions.orders_generation import generate_orders
from multiprocessing import Pool
import os
from itertools import product
import pandas as pd
from results.worker import init_worker, full_optimisation_model




def build_tasks(orders_list, A, B, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, backtrack_penalty, time_limit):
    for order_set_idx, num_aisles, num_bays in product(range(len(orders_list)), A, B):
        num_products = num_aisles*num_bays*slot_capacity
        order_size = len(orders_list[order_set_idx])

        if num_products < order_size:
            continue

        cluster_max_dist = num_bays/2

        yield (
            order_set_idx,
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



def run(product_df, orders_list, A, B, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, backtrack_penalty, time_limit, chunksize):
    
    tasks = build_tasks(orders_list=orders_list,
                        A = A,
                        B = B,
                        slot_capacity = slot_capacity,
                        between_aisle_dist = between_aisle_dist,
                        between_bay_dist = between_bay_dist,
                        crushing_multiple = crushing_multiple,
                        backtrack_penalty = backtrack_penalty,
                        time_limit = time_limit
                        )
    
    num_workers = os.environ.get("SLURM_CPUS_PER_TASK", os.cpu_count() or 1)

    with Pool(
        processes=num_workers,
        initializer=init_worker,
        initargs=(product_df, orders_list),
    ) as p:
        rows = p.starmap(full_optimisation_model, tasks, chunksize=chunksize)

    df = pd.DataFrame(rows)

    return df


def main(A, B, O, Q, slot_capacity, between_aisle_dist, between_bay_dist, crushing_multiple, backtrack_penalty, time_limit, chunksize, seed):
    product_df = pd.read_parquet("data/prod_df.parquet")
    C = [2*a*b for a in A for b in B]
    orders_list = [generate_orders(o, q, num_products, seed) for o in O for q in Q for num_products in C if num_products >= q]

    df = run(product_df = product_df,
             orders_list = orders_list,
             A = A,
             B = B,
             slot_capacity = slot_capacity,
             between_aisle_dist = between_aisle_dist,
             between_bay_dist = between_bay_dist,
             crushing_multiple = crushing_multiple,
             backtrack_penalty=backtrack_penalty,
             time_limit=time_limit,
             chunksize=chunksize)
    
    df.to_parquet("data/test_output.parquet", index = False)

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

