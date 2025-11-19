import pandas as pd
import numpy as np
from scipy.stats import spearmanr

# importing the dataframe
df = pd.read_csv("output/strict_s_shape_large_instances_single_trial.csv")

# extracting values from the dataframe
R = np.array(df["avg_runtime"])
A = np.array(df["aisles"])
B = np.array(df["bays"])
O = np.array(df["num_orders"])
Q = np.array(df["order_size"])

# creating different measures of instance size
AB = A*B
AO = A*O
AQ = A*Q
BO = B*O
BQ = B*Q
OQ = O*Q
ABO = A*B*O
ABQ = A*B*Q
AOQ = A*O*Q
BOQ = B*O*Q
ABOQ = A*B*O*Q

instance_sizes = [A, B, O, Q, AB, AO, AQ, BO, BQ, OQ, ABO, ABQ, AOQ, BOQ, ABOQ]

# calculating correlations and pvalues
correlations = []
pvalues = []

for size in instance_sizes:
    corr, pval = spearmanr(size, R)
    correlations.append(corr)
    pvalues.append(pval)


data = {
    "instance_size_measure":["A", "B", "O", "Q", "AB", "AO", "AQ", "BO", "BQ", "OQ", "ABO", "ABQ", "AOQ", "BOQ", "ABOQ"],
    "correlation":correlations,
    "pvalue":pvalues
}

df = pd.DataFrame(data)

df.to_csv("output/corr_pval_df.csv")