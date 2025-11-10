import pandas as pd
from typing import Tuple
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib import cm
from matplotlib.colors import Normalize, LinearSegmentedColormap


def plot_product_placement(df: pd.DataFrame, aisles: int, scaled_frequency: dict[int, float]) -> Figure:
    """
    Generates a warehouse figure including product placements, with products shaded based on their demands in orders

    Inputs:
    - df: a pandas dataframe with the assignments of products to slots. This is the fourth output of each of the models
    - aisles: the number of aisles in the warehouse
    - scaled_frequency: the frequency with which products appear in orders, scaled by the max frequency to lie between 0 and 1

    Outputs:
    - figure: a figure of the warehouse with product placements and demands
    """
    
    # Tag each product in a slot with offset index (0 or 1)
    df["offset_idx"] = df.groupby(["aisle", "bay"]).cumcount()

    # Horizontal offset (to avoid overlapping)
    delta = 0.1
    df["aisle_plot"] = df["aisle"] + df["offset_idx"].replace({0: -1, 1: 1}) * delta
    df["bay_plot"] = df["bay"]

    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Vertical aisle lines
    for a in range(1, aisles + 1):
        ax.axvline(x=a, color="gray", linestyle="-", linewidth=1)

    # Prepare colormap
    start_color = "#ffffff"
    end_color = "#0F457A"

    custom_cmap = LinearSegmentedColormap.from_list("custom_gradient",[start_color, end_color])

    norm = Normalize(vmin=0, vmax=1)

    # Get color for each product based on scaled frequency
    df["color"] = df["product"].map(lambda p: custom_cmap(norm(scaled_frequency.get(p, 0))))

    # Scatter plot
    ax.scatter(
        df["aisle_plot"],
        df["bay_plot"],
        s=500,
        color=df["color"],
        edgecolor="k"
    )

    # Product number labels
    for _, row in df.iterrows():
        ax.text(
            row["aisle_plot"],
            row["bay_plot"],
            str(row["product"]), 
            fontsize=7,
            ha="center",
            va="center",
            color="black"
        )

    # Integer ticks
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))

    ax.set_xlabel("Aisle")
    ax.set_ylabel("Row")
    ax.set_title("Product Locations by Demand Frequency")
    ax.grid(False)

    # Add colorbar
    from matplotlib.cm import ScalarMappable
    sm = ScalarMappable(cmap=custom_cmap, norm=norm)
    sm.set_array([])  # optional but avoids deprecation warning
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Scaled Order Frequency")

    plt.show()


def calculate_scaled_freq(prod_num: int, orders: dict) -> Tuple[dict[int,int], dict[int, float]]:
    """
    Calculates the occurence frequency and scaled occurrence frequency of products in orders for 
    use in plotting (to shade products by demand)
    
    Inputs:
    - prod_num: the number of products in the warehouse, calculated as the product of the number 
    of aisles, the number of rows and the slot capacity
    - orders: the dictionary of orders which we are using to generate the solution

    Outputs:
    - occurrence_frequency: the number of times each product appears in the orders dictionary
    - scaled_frequency: the occurrence frequency scaled by the frequency of the most-occurring 
    product to lie between 0 and 1
    """

    occurrence_frequency = {} # initialise a dictionary for order frequencies

    for prod in range(prod_num):
        order_freq = 0
        for order in orders:
            if prod in orders[order]:
                order_freq += 1
        occurrence_frequency[prod] = order_freq

    # calculating the maximum occurrence frequency

    max_freq = 0

    for prod in occurrence_frequency:
        if occurrence_frequency[prod] > max_freq:
            max_freq = occurrence_frequency[prod]

    # calculating scaled occurrence frequencies

    scaled_frequency = {}

    for prod in range(prod_num):
        scaled_frequency[prod] = occurrence_frequency[prod]/max_freq
    
    return occurrence_frequency, scaled_frequency
