import pandas as pd
import numpy as np
import random

def create_data_df(num_prods ,weight_lower, weight_upper, num_clusters, weights_dp = 2, seed = 123):

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