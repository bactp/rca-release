import pandas as pd
from datetime import datetime
import numpy as np


"""
Prediction explaination

Input: data from 25s == 5 samples, e.g., [9:37:10, 9:37:15, 9:37:20, 9:37:25, 9:37:30]
Predict: labels for the next 25s, e.g., [9:37:35, 9:37:40, 9:37:45, 9:37:50, 9:37:55] <- ['normal', 'normal', 'normal', 'incident', 'incident',]

"""


def dl_datetime_format(s):
    s = str(s)
    s = s.split(' ')
    s = f"{s[1]} {s[0]}"
    s = datetime.strptime(s, '%m/%d/%y %H:%M:%S')
    return s


def dl_label_mapping(s):
    return 1 if s.lower() == 'normal' else 0


def dl_make_series_data(df=pd.DataFrame, time_step=int) -> np.array:
    if df.empty:
        raise ValueError("DATA IS EMPTY !!!")
    else:
        df = df.fillna(0)
        df['label'] == df['label'].apply(dl_label_mapping)
        df['timestamp'] = df['timestamp'].apply(dl_datetime_format)
        df = df.groupby('label').resample(f"{time_step}S", on="timestamp")
        df = df.sum()
        df = df.reset_index()
        df = np.array(np.split(df, len(df)/time_step))
        print(f"Shapes (# rows, # samples in a row, # fields in a sample): {df.shape}")
        return df



def dl_evaluate_model():
    pass


def dl_build_model():
    pass


if __name__=="__main__":
    df = pd.read_csv('./data/edge-test-control-plane-8fdld.csv')
    print(df)
    print(dl_make_series_data(df=df, time_step=5))




