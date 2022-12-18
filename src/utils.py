import os
import time
import requests
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
import numpy as np
import src.interpretability_module as interp
import pymongo
import requests
import time
import sys
import pandas as pd


#===========Data collecting and retreiving=========== #
def db_connection():
    """
    create connection to the Mongo database
    """

    request_url = "mongodb://bactp:lovedcn123@192.168.40.246:27017/admin"
    db_name = "Starlab-data"
    myclient = pymongo.MongoClient(request_url)
    mydb = myclient[db_name]
    return mydb

def get_instances_list():
    """
    get the list of instances (i.e. host or virtual machine) in the cluster
    """

    instance_list = []
    try:
        response = requests.get('http://192.168.40.232:31270/api/v1/query', params={'query': 'machine_type'})
        if bool(response.json()['data']['result']):
            instances = response.json()['data']['result']
            for instance in instances:
                instance_list.append(instance['metric']['instance'])
    except:
        instance_list.append(0)
   
    
    print(instance_list)
    return instance_list


def get_instance_metrics(name):
    """
    get metrics for each instance in the instance list
    """

    instance_metrics = {
                        'CPU_utilization': 'sum(rate(node_cpu_seconds_total{mode="idle", instance="' + name + '"}[1m]))',
                        'load_average': 'sum(node_load5{instance="' + name + '"}) / count(node_cpu_seconds_total{instance="' + name + '", mode="system"})*100',
                        'mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + name + '"}) / sum(node_memory_MemTotal_bytes{instance="' + name + '"})*100)',
                        'disk_utilization': '(sum(node_filesystem_size_bytes{instance="' + name + '"}) - sum(node_filesystem_free_bytes{instance="' + name + '"})) / sum(node_filesystem_size_bytes{instance="' + name + '"})*100',
                        'disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + name + '"}[1m]))/1024',
                        'disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + name + '"}[1m]))/1024',
                        'net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + name + '", device="ens3"}[1m]))/1024',
                        'net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + name + '", device="ens3"}[1m]))/1024',
                        'net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + name + '", device="ens3"}[1m]))',
                        'net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + name + '", device="ens3"}[1m]))',
                        'net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + name + '", device="ens3"}[1m]))',
                        'net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + name + '", device="ens3"}[1m]))'
                        }
    metrics = []
    for metric_name, metric_value in instance_metrics.items():
        try:
            response = requests.get('http://192.168.40.232:31270/api/v1/query', params={'query': metric_value})
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                metrics.append(test)
            else:
                metrics.append(0)
        except:
            print("Exception")
        
    return metrics

def data_stream(instance_list):
    """
    construct features of dataset
    """
    data = {}
    for instance in instance_list:
        instance_metrics = get_instance_metrics(instance)

        data.update({
                    instance + '_CPU_utilization': instance_metrics[0],
                    instance + '_load_average': instance_metrics[1],
                    instance + '_mem_utilization': instance_metrics[2],
                    instance + '_disk_utilization': instance_metrics[3],
                    instance + '_disk_read': instance_metrics[4],
                    instance + '_disk_write': instance_metrics[5],
                    instance + '_net_rx': instance_metrics[6],
                    instance + '_net_tx': instance_metrics[7],
                    instance + '_net_rx_drop': instance_metrics[8],
                    instance + '_net_tx_drop': instance_metrics[9],
                    instance + '_net_rx_err': instance_metrics[10],
                    instance + '_net_tx_err': instance_metrics[11]
                    })
    
    
    data.update({
                 'timestamp': time.strftime('%X %x %Z'),
                 'label': '1'
                })
    return data


# def data_stream_vm_split(instance, label):
#     """
#     construct features of dataset
#     """
#     data = {}
#     instance_metrics = get_instance_metrics(instance)

#     data.update({
#                 '_CPU_utilization': instance_metrics[0],
#                 '_load_average': instance_metrics[1],
#                 '_mem_utilization': instance_metrics[2],
#                 '_disk_utilization': instance_metrics[3],
#                 '_disk_read': instance_metrics[4],
#                 '_disk_write': instance_metrics[5],
#                 '_net_rx': instance_metrics[6],
#                 '_net_tx': instance_metrics[7],
#                 '_net_rx_drop': instance_metrics[8],
#                 '_net_tx_drop': instance_metrics[9],
#                 '_net_rx_err': instance_metrics[10],
#                 '_net_tx_err': instance_metrics[11]
#                 })


#     data.update({
#                 'timestamp': time.strftime('%X %x %Z'),
#                 'label': label
#                 })
    
#     save_data_to_db(data_collection_name=instance, data=data)
#     return data

def save_data_to_db(data_collection_name: str, data: list):
    if len(data) == 0:
        raise ValueError("SAVE TO DB: DATA IS EMPTY !!!")
    else:
        mydb = db_connection()
        mycon = mydb[data_collection_name]
        info = mycon.insert_one(data)
        print(info.inserted_id, "collect metrics successfully!")


def data_save_vm_split(instance_list, label):
    """
    save real-time data by each instance (VM or host)
    """
    for instance in instance_list:
        # data_stream_vm_split(instance=instance, label=label)
        data = {}
        instance_metrics = get_instance_metrics(instance)
        data.update({
                '_CPU_utilization': instance_metrics[0],
                '_load_average': instance_metrics[1],
                '_mem_utilization': instance_metrics[2],
                '_disk_utilization': instance_metrics[3],
                '_disk_read': instance_metrics[4],
                '_disk_write': instance_metrics[5],
                '_net_rx': instance_metrics[6],
                '_net_tx': instance_metrics[7],
                '_net_rx_drop': instance_metrics[8],
                '_net_tx_drop': instance_metrics[9],
                '_net_rx_err': instance_metrics[10],
                '_net_tx_err': instance_metrics[11]
                })


        data.update({
                    'timestamp': time.strftime('%X %x %Z'),
                    'label': label
                    })
        save_data_to_db(data_collection_name=instance, data=data)
    
    print("Save all instances finished !!!")

def data_save_all_in_one(data_samples, data_collection_name):
    """
    store data samples collected from data_stream() into the database to create training dataset
    """
    mydb = db_connection()
    mycon = mydb[data_collection_name]
    info = mycon.insert_one(data_samples)
    print(info.inserted_id, "new training samples added successfully!")

    
#===========TRAINING PHASE=========== #
def load_data_from_db(data_collection_name):
    """
    load training data from mino database and convert to DataFrame
    """
    my_db = db_connection()
    data = my_db[data_collection_name].find()
    data_df = pd.DataFrame(list(data))
    return data_df


def tp_load_data(fp: str) -> pd.DataFrame:
    df = pd.read_csv(fp)
    if df.empty:
        raise ValueError("Empty data !!!")
    else:
        return df


def tp_preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    clear_nan = df.fillna(0)
    return clear_nan


def create_model(params: dict):
    iforest = IsolationForest(**params)
    return iforest


def train_model(model, feature: pd.DataFrame):
    if feature.empty:
        raise ValueError("Empty features !!!")
    else:
        print(f"Model params: {model.get_params()}")
        print("==========TRAINING STARTED==========")
        tmp_model = model.fit(feature)
        print("==========TRAINING FINISHED==========")
        return tmp_model


def save_model(model, fp: str, name: str) -> str:
    filename = os.path.join(fp, f'{name}.sav')
    joblib.dump(model, filename)
    print("==========MODEL SAVED==========")
    print(f"Saved path: {filename}")
    return filename


# =========SERVING PHASE========== #

def sp_preprocess_data():
    pass


def load_model(fp: str):
    if fp == '':
        raise ValueError("INVALID VALUE !!!")
    elif 'sav' not in fp:
        raise ValueError("INVALID MODEL PATH: \'sav\' not included !!!")
    else:
        return joblib.load(fp)


def predict(model, df: pd.DataFrame) -> pd.DataFrame:
    """
    The anomaly score of the input samples. The lower, the more abnormal.
    Negative scores represent outliers, positive scores represent inliers.
    """
    if df.empty:
        raise ValueError("EMPTY DATA !!!")
    else:
        preds = np.array(model.decision_function(df) < 0).astype('int')
        preds = pd.DataFrame(preds, columns=['abnormal_score'])
        return preds



def visualize(predictions: pd.DataFrame, df: pd.DataFrame, cols: list):
    if predictions.empty or df.empty:
        raise ValueError("PREDICTIONS OR FEATURE DATA IS EMPTY !!!")
    else:
        tmp_df = pd.concat([df[cols], predictions], axis=1)
        return tmp_df

    # ...


def local_diffi_batch(model, arr: np.ndarray):
    fi = []
    ord_idx = []
    exec_time = []
    for i in range(arr.shape[0]):
        x_curr = arr[i, :]
        fi_curr, exec_time_curr = interp.local_diffi(model, x_curr)
        fi.append(fi_curr)
        ord_idx_curr = np.argsort(fi_curr)[::-1]
        ord_idx.append(ord_idx_curr)
        exec_time.append(exec_time_curr)
    fi = np.vstack(fi)
    ord_idx = np.vstack(ord_idx)
    return fi, ord_idx, exec_time


def top_map(model, k: int, arr: np.ndarray):
    importance_score, feature_index, _ = local_diffi_batch(model=model, arr=arr)
    dict_list = []
    for idx_lst, imp_lst in zip(feature_index, importance_score):
        d = {}
        for idx, imp in zip(idx_lst, imp_lst):
            d[idx] = imp
        sorted_d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
        topk_d = dict(list(sorted_d.items())[0: k])
        dict_list.append(topk_d)
    return dict_list


# def get_most_appeared_feature(imp_dict: [dict]) -> list:
#     items = []
#     temp = []
#     for d in imp_dict:
#         for k, _ in d.items():
#             items.append(k)
#     items_occ = dict((x, items.count(x)) for x in set(items))
#     sorted_items_occ = {k: v for k, v in sorted(items_occ.items(), key=lambda item: item[1], reverse=True)}
#
#     for k, _ in sorted_items_occ.items():
#         temp.append(k)
#     return temp


def map_feature_name(d: dict) -> dict:
    map_d = {}
    for k, v in d.items():
        for K, V in FEATURE_IDX.items():
            if k == K:
                map_d[V] = v
    return map_d


def trigger():
    pass


# def compensation(ab_score: dict, topk: int):
#     w_dict = {
#         "compute": 0.86,
#         "vm": 0.12,
#         "host": 0.02
#     }

#     for k, v in ab_score.items():
#         if "compute" in k:
#             ab_score[k] = (ab_score[k] * w_dict["compute"]) / 2
#         elif "vm" in k:
#             ab_score[k] = (ab_score[k] * w_dict["vm"]) / 2
#         else:
#             ab_score[k] = (ab_score[k] * w_dict["host"]) / 2

#         sorted_d = {k: v for k, v in sorted(ab_score.items(), key=lambda item: item[1], reverse=True)}
#         topk_d = dict(list(sorted_d.items())[0: topk])
#     return topk_d




