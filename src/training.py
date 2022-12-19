from src.utils import *
import json
from flask import Flask, request, jsonify
from http import HTTPStatus




#====training====

def training(data: pd.DataFrame, params: dict, saved_path: str, model_name:str):
    
    # data_path = 'data/training_data_2.csv'
    # params = {'n_estimators': 100, 'max_samples': 64, 'contamination': 'auto', 'random_state': 0, 'bootstrap': False}
    # saved_path = 'model'
    # data = data_path
    feature = data.loc[:, ~data.columns.isin(['timestamp', '_id', 'label'])].copy()
    feature = tp_preprocess_data(df=feature)
    feature = feature.reindex(columns=sorted(feature.columns))
    print(feature.shape)
    feature = df_normalize(df=feature)
    iforest = create_model(params=params)
    trained_iforest = train_model(model=iforest, feature=feature)
    fp = save_model(model=trained_iforest, fp=saved_path, name=model_name)
    return fp


