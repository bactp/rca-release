import sys
import os
import time
sys.path.append(os.path.abspath('src'))
from src.utils import *
from src.training import *
from src.serving import *
# from flask import Flask, request, jsonify
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
    print(data_collection_name)

    train_data = load_data_from_db(data_collection_name)
    print(train_data)
    # feature = train_data.loc[:, train_data.columns != 'timestamp'].copy()
    # feature = tp_preprocess_data(df=feature)
    training(data_path=train_data, params=params, saved_path=saved_path, model_name=model_name)
    result = {"retraining": "Done"}
    return jsonify(result), HTTPStatus.CREATED
   
def run_flask_server():
       api.run(host='0.0.0.0', port=6868)

if __name__ == "__main__":
    # loaded_model = load_model(fp=f'model/model5.sav')
    t1 = threading.Thread(target=run_flask_server)
    t1.start()
    # instance_list = get_instances_list()
    # data_collection_name = "training_data"
    
    # while True:
    #     sp_data = merge_data(instance_list)
    #     collect_training_data(sp_data, data_collection_name)
    #     # data_df = pd.DataFrame([sp_data])
    #     # data_df = data_df.reindex(columns=sorted(data_df.columns))
    #     #save to db

    #     #serving
    #     # feature = data_df.loc[:, data_df.columns != 'timestamp'].copy()
    #     # feature = tp_preprocess_data(df=feature)

    #     # serving(model=loaded_model, feature=feature)

    #     time.sleep(5)

    # test slicing window
    while True:
        d = {'time': time.strftime('%X %x %Z'), 'a': 1, 'b': 32}
        df = slice_df(input=d, df_name='series_df')
        # print(df)
        time.sleep(5)