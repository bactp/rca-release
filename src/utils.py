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


FEATURE_IDX = {0: 'catalogue_cpu_cfs_periods_total', 1: 'catalogue_cpu_cfs_throttled', 2: 'catalogue_cpu_usage', 3: 'catalogue_mem_usage', 4: 'catalogue_net_rx_byte',
               5: 'catalogue_net_rx_drop', 6: 'catalogue_net_rx_error', 7: 'catalogue_net_tx_byte', 8: 'catalogue_net_tx_drop', 9: 'catalogue_net_tx_error',
               10: 'front-end_cpu_cfs_periods_total', 11: 'front-end_cpu_cfs_throttled', 12: 'front-end_cpu_usage', 13: 'front-end_mem_usage', 14: 'front-end_net_rx_byte',
               15: 'front-end_net_rx_drop', 16: 'front-end_net_rx_error', 17: 'front-end_net_tx_byte', 18: 'front-end_net_tx_drop', 19: 'front-end_net_tx_error',
               20: 'hyungnam-worker1_CPU_utilization', 21: 'hyungnam-worker1_disk_read', 22: 'hyungnam-worker1_disk_utilization', 23: 'hyungnam-worker1_disk_write',
               24: 'hyungnam-worker1_load_average', 25: 'hyungnam-worker1_mem_utilization', 26: 'hyungnam-worker1_net_rx', 27: 'hyungnam-worker1_net_rx_drop',
               28: 'hyungnam-worker1_net_rx_err', 29: 'hyungnam-worker1_net_tx', 30: 'hyungnam-worker1_net_tx_drop', 31: 'hyungnam-worker1_net_tx_err',
               32: 'hyungnam-worker2_CPU_utilization', 33: 'hyungnam-worker2_disk_read', 34: 'hyungnam-worker2_disk_utilaization', 35: 'hyungnam-worker2_disk_write',
               36: 'hyungnam-worker2_load_average', 37: 'hyungnam-worker2_mem_utilization', 38: 'hyungnam-worker2_net_rx', 39: 'hyungnam-worker2_net_rx_drop',
               40: 'hyungnam-worker2_net_rx_err', 41: 'hyungnam-worker2_net_tx', 42: 'hyungnam-worker2_net_tx_drop', 43: 'hyungnam-worker2_net_tx_err',
               44: 'hyungnam-worker3_CPU_utilization', 45: 'hyungnam-worker3_disk_read', 46: 'hyungnam-worker3_disk_utilaization', 47: 'hyungnam-worker3_disk_write',
               48: 'hyungnam-worker3_load_average', 49: 'hyungnam-worker3_mem_utilization', 50: 'hyungnam-worker3_net_rx', 51: 'hyungnam-worker3_net_rx_drop',
               52: 'hyungnam-worker3_net_rx_err', 53: 'hyungnam-worker3_net_tx', 54: 'hyungnam-worker3_net_tx_drop', 55: 'hyungnam-worker3_net_tx_err',
               56: 'incoming_success_rate', 57: 'latency', 58: 'orders_cpu_cfs_periods_total', 59: 'orders_cpu_cfs_throttled', 60: 'orders_cpu_usage',
               61: 'orders_mem_usage', 62: 'orders_net_rx_byte', 63: 'orders_net_rx_drop', 64: 'orders_net_rx_error', 65: 'orders_net_tx_byte', 66: 'orders_net_tx_drop',
               67: 'orders_net_tx_error', 68: 'payment_cpu_cfs_periods_total', 69: 'payment_cpu_cfs_throttled', 70: 'payment_cpu_usage', 71: 'payment_mem_usage',
               72: 'payment_net_rx_byte', 73: 'payment_net_rx_drop', 74: 'payment_net_rx_error', 75: 'payment_net_tx_byte', 76: 'payment_net_tx_drop', 77: 'payment_net_tx_error',
               78: 'queue-master_cpu_cfs_periods_total', 79: 'queue-master_cpu_cfs_throttled', 80: 'queue-master_cpu_usage', 81: 'queue-master_mem_usage',
               82: 'queue-master_net_rx_byte', 83: 'queue-master_net_rx_drop', 84: 'queue-master_net_rx_error', 85: 'queue-master_net_tx_byte', 86: 'queue-master_net_tx_drop',
               87: 'queue-master_net_tx_error', 88: 'request_per_second', 89: 'shipping_cpu_cfs_periods_total', 90: 'shipping_cpu_cfs_throttled', 91: 'shipping_cpu_usage',
               92: 'shipping_mem_usage', 93: 'shipping_net_rx_byte', 94: 'shipping_net_rx_drop', 95: 'shipping_net_rx_error', 96: 'shipping_net_tx_byte', 97: 'shipping_net_tx_drop',
               98: 'shipping_net_tx_error', 99: 'starlab-compute03_CPU_utilization', 100: 'starlab-compute03_disk_read', 101: 'starlab-compute03_disk_utilization',
               102: 'starlab-compute03_disk_write', 103: 'starlab-compute03_load_average', 104: 'starlab-compute03_mem_utilization', 105: 'starlab-compute03_net_rx_drop_eno1',
               106: 'starlab-compute03_net_rx_drop_eno2', 107: 'starlab-compute03_net_rx_eno1', 108: 'starlab-compute03_net_rx_eno2', 109: 'starlab-compute03_net_rx_err_eno1',
               110: 'starlab-compute03_net_rx_err_eno2', 111: 'starlab-compute03_net_tx_drop_eno1', 112: 'starlab-compute03_net_tx_drop_eno2', 113: 'starlab-compute03_net_tx_eno1',
               114: 'starlab-compute03_net_tx_eno2', 115: 'starlab-compute03_net_tx_err_eno1', 116: 'starlab-compute03_net_tx_err_eno2', 117: 'starlab-compute03_temp_cel',
               118: 'starlab-compute04_CPU_utilization', 119: 'starlab-compute04_disk_read', 120: 'starlab-compute04_disk_utilization', 121: 'starlab-compute04_disk_write',
               122: 'starlab-compute04_load_average', 123: 'starlab-compute04_mem_utilization', 124: 'starlab-compute04_net_rx_drop_eno1', 125: 'starlab-compute04_net_rx_drop_eno2',
               126: 'starlab-compute04_net_rx_eno1', 127: 'starlab-compute04_net_rx_eno2', 128: 'starlab-compute04_net_rx_err_eno1', 129: 'starlab-compute04_net_rx_err_eno2',
               130: 'starlab-compute04_net_tx_drop_eno1', 131: 'starlab-compute04_net_tx_drop_eno2', 132: 'starlab-compute04_net_tx_eno1', 133: 'starlab-compute04_net_tx_eno2',
               134: 'starlab-compute04_net_tx_err_eno1', 135: 'starlab-compute04_net_tx_err_eno2', 136: 'starlab-compute04_temp_cel', 137: 'timestamp'}

#===========Data collecting and retreiving=========== #
def db_connection():
    """
    create connection to the Mongo database
    """

    request_url = "mongodb://bactp:lovedcn123@192.168.40.246:27017/admin"
    db_name = "RCA"
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
                        'CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + name + '"}[1m])) * 100)',
                        'load_average': 'sum(node_load5{instance="' + name + '"}) / count(node_cpu_seconds_total{instance="' + name + '", mode="system"})*100',
                        'mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + name + '"}) / sum(node_memory_MemTotal_bytes{instance="' + name + '"})*100)',
                        'disk_utilization': '(sum(node_filesystem_size_bytes{instance="' + name + '"}) - sum(node_filesystem_free_bytes{instance="' + name + '"})) / sum(node_filesystem_size_bytes{instance="' + name + '"})*100',
                        'disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + name + '"}[1m]))/1024',
                        'disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + name + '"}[1m]))/1024',
                        'net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + name + '", device="eth0"}[1m]))/1024',
                        'net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + name + '", device="eth0"}[1m]))/1024',
                        'net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + name + '", device="eth0"}[1m]))',
                        'net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + name + '", device="eth0"}[1m]))',
                        'net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + name + '", device="eth0"}[1m]))',
                        'net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + name + '", device="eth0"}[1m]))',
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

def merge_data(instance_list):
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
                 'timestamp': time.strftime('%X %x %Z')
                })
    return data

def collect_training_data(data_samples, data_collection_name):
    """
    store data samples collected from merge_data() into the database to create training dataset
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


def rule_based_model(df):
    """
    =====NET=====
    compute04-net, vm2-net, vm3-net
    """
    compute04_net = df["starlab-compute04_net_rx_eno1"].item()
    vm2_net = df["hyungnam-worker1_net_rx"].item()
    vm3_net = df["hyungnam-worker3_net_rx"].item()

    if compute04_net == 0:
        if vm2_net == 0 & vm3_net == 0:
            return 1
    else:
        return 0

    pass


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


def compensation(ab_score: dict, topk: int):
    w_dict = {
        "compute": 0.86,
        "vm": 0.12,
        "host": 0.02
    }

    for k, v in ab_score.items():
        if "compute" in k:
            ab_score[k] = (ab_score[k] * w_dict["compute"]) / 2
        elif "vm" in k:
            ab_score[k] = (ab_score[k] * w_dict["vm"]) / 2
        else:
            ab_score[k] = (ab_score[k] * w_dict["host"]) / 2

        sorted_d = {k: v for k, v in sorted(ab_score.items(), key=lambda item: item[1], reverse=True)}
        topk_d = dict(list(sorted_d.items())[0: topk])
    return topk_d


def slice_df(input: dict, df_name: str) -> pd.DataFrame:
    if not os.path.isdir('./data'):
        os.makedirs('./data')
    
    try:
        df = pd.read_csv(f'./data/{df_name}.csv')
        if df.shape[0] == 5:
            tmp_df = pd.DataFrame([input])
            df = pd.concat([df, tmp_df], ignore_index=True)
            df = df.loc[1:]
            df.to_csv(f'./data/{df_name}.csv', index=0)
            return df
        elif df.shape[0] < 5:
            tmp_df = pd.DataFrame([input])
            df = pd.concat([df, tmp_df], ignore_index=True)
            df.to_csv(f'./data/{df_name}.csv', index=0)
            return df
        else:
            raise ValueError("MORE THAN 5 EVENTS IN THE DATAFRAME !!!")
    except:
        df = pd.DataFrame([input])
        df.to_csv(f'./data/{df_name}.csv', index=0)
        return df


