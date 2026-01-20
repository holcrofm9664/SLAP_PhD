import pandas as pd
import numpy as np
import random

def create_data_df(num_prods:int ,weight_lower:float, weight_upper:float, num_clusters:int, weights_dp:int = 2, seed:int = 123) -> None:
    """
    Creates a synthetic product dataframe including product id, weight and cluster

    Inputs:
    - num_prods: the number of products we wish to have in our warehouse. Usually, this is equal to the number of slots (num_aisles * num_bays * slot_capacity)
    - weights_lower: the minimum weight we would like to assign to a product
    - weights_upper: the maximum weight we would like to assign to a product
    - num_clusters: the number of clusters we would like our products to be divided across
    - weights_dp: the number of decimal places we would like for products to be rounded to. The standard is 2
    - seed: the seed used to generate the product attributes. The standard is 123

    Outputs:
    - create a pandas dataframe with product id, weight and cluster, and saves this as a .parquet file
    """
    
    random.seed(seed)
    
    prod_ids = np.arange(1, num_prods+1)

    prod_weights = np.round(np.random.uniform(weight_lower, weight_upper, num_prods), weights_dp)

    prod_clusters = np.random.randint(1,num_clusters+1,num_prods)

    prod_dict = {
        "prod_id":prod_ids,
        "prod_weight":prod_weights,
        "prod_cluster":prod_clusters
    }

    prod_df = pd.DataFrame(prod_dict)

    prod_df.to_parquet("data/prod_df.parquet", engine = "fastparquet")