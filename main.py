import sys
import os
import time
sys.path.append(os.path.abspath('src'))
from src.utils import *
from src.training import *
from src.serving import *
from flask import Flask, request, jsonify
from http import HTTPStatus
from datetime import datetime

import threading

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

api = Flask(__name__)
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

@api.route('/model/training', methods=['POST'])
def retraining():
    """
    retraining the model with new dataset
    parameter for retraining model
    {
        "model_params": {
                        "n_estimators": 200,
                        "max_samples": 300,
                        "contamination": 'auto',
                        "random_state": 0,
                        "bootstrap": False
                        },
        "model_name": "lastest",
        "data_collection_name": "training_data",
    }
    """
    saved_path = 'model'
    # Check body json
    if not request.data:
        return jsonify({"error":"Empty body"}), HTTPStatus.BAD_REQUEST
    # Required body must a valid json
    if not is_json(request.data):
        return jsonify({"error":"Not a valid json body"}), HTTPStatus.BAD_REQUEST
    request_json = request.get_json() 
    
    
    params = {
                'n_estimators': request_json["model_params"]["n_estimators"],
                'max_samples': request_json["model_params"]["max_samples"],
                'contamination': request_json["model_params"]["contamination"],
                'random_state': request_json["model_params"]["random_state"],
                'bootstrap': request_json["model_params"]["bootstrap"]
            }


    model_name = request_json["model_name"]
    data_collection_name = request_json["data_collection_name"]

    train_data = load_data_from_db(data_collection_name)
    print(train_data)
    training(data=train_data, params=params, saved_path=saved_path, model_name=model_name)
    result = {"retraining": "Done"}
    return jsonify(result), HTTPStatus.CREATED

@api.route('/rca', methods=['POST'])
def listening_damage_instane():
    print(request)
    if not request.data:
        return jsonify({"error":"Empty body"}), HTTPStatus.BAD_REQUEST
    # Required body must a valid json
    if not is_json(request.data):
        return jsonify({"error":"Not a valid json body"}), HTTPStatus.BAD_REQUEST
    incident_detected = request.get_json()
    file1 = open("myfile.txt", "w+") 
    print("Incident detected instance :" + str(incident_detected["data"][0]))
    file1.write(incident_detected["data"][0])
    file1.close() 
    # print(datetime.utcnow().strftime('%F %T.%f')[:-3])
    return incident_detected, HTTPStatus.CREATED

def run_flask_server():
       api.run(host='0.0.0.0', port=9999)


if __name__ == "__main__": 

    t1 = threading.Thread(target=run_flask_server)
    t1.start()
    
    params = {'n_estimators': 300, 'max_samples': 1024,'max_features': 12, 'contamination': 0.035, 'random_state': 0, 'bootstrap': False}
    saved_path = 'model'
    model_name = 'lastest'
    train_data = load_data_from_db("training_data_by_feature_2")
    # training(train_data, params=params, saved_path=saved_path, model_name=model_name)
    loaded_model = load_model(f'model/{model_name}.sav')
    instance_list = get_instances_list()
    
    new_list = []
    for instance in instance_list:
        if instance[0:9] != 'edge-test':
            new_list.append(instance)
    instance_list = new_list
    
    while True:
    #     #====serving-prediction===
        time.sleep(20)
        incident_list, incident_df_list = serving_by_instance(instance_list=instance_list, model=loaded_model)
        if len(incident_list)==0:
            print(time.strftime('%X %x %Z') + ": Normal")
            time.sleep(10)
            continue
        else:
            # print(incident_list)
            incident_cluster = incident_list[0]
            if 'edge' in incident_cluster:
               prediction_mess(incident_cluster[0:14])
            else:
                prediction_mess(incident_cluster[0:10])


    #     #====serving-rca====
        incident_detected = ""
        file2 = open("myfile.txt", "r") 
        i = 0
        while True and i < 36:
            i = i + 1
            time.sleep(10)
            incident_detected = file2.read()
            if incident_detected != "":
                print("-------------------")
                print(incident_detected)
                file2.close()
                break

    
        data = data_stream_instance(incident_detected)
        data_df = pd.DataFrame([data])
        data_df = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label', 'id'])]
        FEATURE_IDX = get_feature_index(data_df)
        root_observed = serving_rca(model=loaded_model, data_df=data_df, feature_idx=FEATURE_IDX)
        root_observed = json.dumps(root_observed, indent = 4) 
        print(root_observed)
        time.sleep(120)

# #===collect training data===
        # data_stream = data_stream_all(instance_list)
        # data_save_all_in_one(data_stream, "all-in-one")
        # for instance in instance_list:
        #     print(instance)
        #     data = data_stream_instance(instance)
        #     save_data_to_db(data_collection_name='training_data_by_feature_2', data=data)
# 

        
