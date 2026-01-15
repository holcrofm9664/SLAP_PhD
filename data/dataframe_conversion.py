import json
import pandas as pd

def read_in_parquet_dataframe(dataframe_path:str):
    df = pd.read_parquet(dataframe_path)

    def json_to_slot_dict(s):
        if isinstance(s, str):
            d = json.loads(s)
            # convert str keys → int, lists → tuples
            return {int(k): tuple(v) for k, v in d.items()}
        return None

    df["slot_assignments_dict"] = df["slot_assignments_dict"].apply(json_to_slot_dict)

    return df