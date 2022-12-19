import sys
import os
import time
sys.path.append(os.path.abspath('src'))
from src.utils import *
from src.training import *
from src.serving import *
from flask import Flask, request, jsonify
from http import HTTPStatus

import threading


# data_path = 'data/training_data5.csv'
# params = {'n_estimators': 200, 'max_samples': 300, 'contamination': 'auto', 'random_state': 0, 'bootstrap': False}
# saved_path = 'model'
# model_name = 'model5'

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
    # print(data_collection_name)

    train_data = load_data_from_db(data_collection_name)
    print(train_data)
    training(data=train_data, params=params, saved_path=saved_path, model_name=model_name)
    result = {"retraining": "Done"}
    return jsonify(result), HTTPStatus.CREATED

@api.route('/rca', methods=['POST'])
def listening_damage_instane():
    if not request.data:
        return jsonify({"error":"Empty body"}), HTTPStatus.BAD_REQUEST
    # Required body must a valid json
    if not is_json(request.data):
        return jsonify({"error":"Not a valid json body"}), HTTPStatus.BAD_REQUEST
    request_json = request.get_json()
    print(request_json)
    result = {"retraining": "Done"}
    return jsonify(result), HTTPStatus.CREATED

def run_flask_server():
       api.run(host='0.0.0.0', port=9999)


if __name__ == "__main__": 
    #====re-trainining-api====
    t1 = threading.Thread(target=run_flask_server)
    t1.start()
    
    #====training-api====
    # train_data = load_data_from_db("training_set_by_feature")
    df = pd.read_csv('data/training_data_by_feature.csv')
    params = {'n_estimators': 200, 'max_samples': 300, 'contamination': 'auto', 'random_state': 0, 'bootstrap': False}
    saved_path = 'model'
    model_name = 'instance_model'
    training(data=df, params=params, saved_path=saved_path, model_name=model_name)
    loaded_model = load_model(fp=f'model/{model_name}.sav')
    # df = df.loc[:, ~df.columns.isin(['timestamp', 'label'])].copy()
    # print(predict(model=loaded_model, df=df).value_counts())
    instance_list = get_instances_list()
    while True:
        
        #===collect training data===
        for instance in instance_list:
            data = data_stream_instance(instance)
            print(data)
            save_data_to_db(data_collection_name='training_data_by_feature', data=data)
            time.sleep(5)
        

    #     # print(FEATURE_IDX)
    #     """
    #     collect-training-data
    #     """
    #     # for instance in instance_list:
    #     #     data = data_stream_instance(instance)
    #     #     save_data_to_db("training_set_by_feature", data)
    #     # print(sp_data)
    #     # serving_rca(model=loaded_model, data_df=sp_data, feature_idx=FEATURE_IDX)
        
    #     # break
    #     #====serving-prediction===
    #     incident_list, incident_df_list = serving_by_instance(instance_list=instance_list, model=loaded_model)
    #     print(incident_list)
    #     # print(incident_df_list)
    #     prediction_mess(incident_list)

    #     # ====check-detection-condition===
    #     incident_detected = []
    #     incident_data = []

    #     print(incident_list)
    #     for instance, data in zip(incident_list, incident_df_list):
    #         check_condition = check_condition(instance)
    #         if check_condition == 0:
    #             incident_detected.append(instance)
    #             incident_data.append(data)
    #         else:
    #             pass
        
    #     if len(incident_detected) == 0:
    #         print(0000)
    #         for instance in instance_list:
    #             check_condition = check_condition(instance)
    #             if check_condition == 0:
    #                 incident_detected.append(instance)
    #                 data =  data_stream_instance(instance)
    #                 data_df =  pd.DataFrame([data])
    #                 data_df = data_df.reindex(columns=sorted(data_df.columns))
    #                 feature = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label'])].copy()
    #                 feature = tp_preprocess_data(df=feature)
    #                 incident_data.append(data)
    #     #trar về root case

    #     assert len(incident_detected) == len(incident_data), "len(incident_detected) has to be equal to len(incident_data)"

    #     # feature importance for each incident instance

    #     for instance, data in zip(incident_detected, incident_data): 
    #         FEATURE_IDX = get_feature_index(data)
    #         rca_mess = serving_rca(model=loaded_model, data_df=data, feature_idx=FEATURE_IDX)
    #         rca_mess.update({"objects": instance})
    #         rca_mess = json.dumps(rca_mess, indent=4)
    #         print(rca_mess)
    #         # recovery_message = {
    #         #                     "time": time.strftime('%X %x %Z'),
    #         #                     "status": "Incident",
    #         #                     "objects": incident_detected,
    #         #                     "potential_root_cause": "root case"
    #         #                    }
        

    #     #====serving-rca====

        
