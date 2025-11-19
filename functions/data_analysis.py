import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# creating a dataframe from our saved results
df = pd.read_csv("strict_s_shape_large_instances_single_trial.csv")

# extracting values from the dataframe and turning to numpy arrays
R = np.array(df["avg_runtime"])
A = np.array(df["aisles"])
B = np.array(df["bays"])
O = np.array(df["num_orders"])
Q = np.array(df["order_size"])

# creating the interaction lists we will need
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

Combinations = [A, B, O, Q, AB, AO, AQ, BO, BQ, OQ, ABO, ABQ, AOQ, BOQ, ABOQ]
names = ["A","B","O","Q","AB","AO","AQ","BO","BQ","OQ","ABO","ABQ","AOQ","BOQ","ABOQ"]


correlations = []
pvalues = []

print(len(R))
for i in range(len(Combinations)):
    print(len(Combinations[i]))
    correlation, pvalue = spearmanr(Combinations[i], R)
    correlations.append(correlation)
    pvalues.append(pvalue)

data = {
    "names":names,
    "correlations":correlations,
    "pvalues":pvalues
}

df_correlation = pd.DataFrame(data)

print(df_correlation)