import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("output/strict_s_shape_large_instances_single_trial.csv")

R = np.array(df["avg_runtime"])
A = np.array(df["aisles"])
B = np.array(df["bays"])
O = np.array(df["num_orders"])
Q = np.array(df["order_size"])

fig, axes = plt.subplots(2,2,figsize = (10,8))

plt.subplots_adjust(hspace=0.3)

axes[0,0].scatter(A, R)
axes[0,0].set_title("Runtimes vs Aisles")
axes[0,0].set_xlabel("aisles")
axes[0,0].set_ylabel("runtime")

axes[0,1].scatter(B, R)
axes[0,1].set_title("Runtimes vs Bays")
axes[0,1].set_xlabel("bays")

axes[1,0].scatter(O, R)
axes[1,0].set_title("Runtimes vs Number of Orders")
axes[1,0].set_xlabel("num_orders")
axes[1,0].set_ylabel("runtime")

axes[1,1].scatter(Q, R)
axes[1,1].set_title("Runtimes vs Order Size")
axes[1,1].set_xlabel("order_size")

plt.show()