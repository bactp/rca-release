import json
import requests
from src.utils import *

def message(d: dict):
    """
    Create message for root cause resulting and recovery triggering
    """
    tmp_lst = [k for k, _ in d.items()]
    unq_prefix = set([k.split('_')[0] for k in tmp_lst])
    tmp_d = {}
    for k in unq_prefix:
        tmp_d[k] = 0
    
    for k in unq_prefix:
        for i in tmp_lst:
            if i.startswith(k):
                tmp_d[k] += 1
    sorted_d = {k: v for k, v in sorted(tmp_d.items(), key=lambda item: item[1], reverse=True)}
    topk_d = dict(list(sorted_d.items())[0: 1])
    msg = list(topk_d.keys())[0]
    return msg


def serving_by_instance(instance_list, model):
    """
    Make prediction real-time and trigger recovery
    """
    incident_list = []
    incident_df_list = []
    for instance in instance_list:
        data =  data_stream_instance(instance)
        data_df =  pd.DataFrame([data])
        data_df = data_df.reindex(columns=sorted(data_df.columns))
        feature = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label'])].copy()
        feature = tp_preprocess_data(df=feature)

        abnormal_points = predict(model=model, df=feature)
        if abnormal_points['abnormal_score'].item() == 1: # 1: normal, 0: abnormal
            print("Anomalous Predicted !!!")
            print(instance)
            incident_list.append(instance)
            incident_df_list.append(feature)
    
    return incident_list, incident_df_list

def prediction_mess(incident_list):
    if len(incident_list)==0:
        pass
    else:
        predict_mess = {
                    "time": time.strftime('%X %x %Z'),
                    "status": "Incident",
                    "potential_objects": incident_list
                }
        request_body = json.dumps(predict_mess, indent=4)
        print(request_body)
        response = send_request("http://127.0.0.1:5000/manager/RCAs", request_body)



def serving_rca(model, data_df: pd.DataFrame, feature_idx: dict):
    """
    Make detection real-time and root cause analysis
    """
    data_df = data_df.reindex(columns=sorted(data_df.columns))
    print(data_df)
    
    feature = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label', 'id'])].copy()
    feature = tp_preprocess_data(df=feature)

    abnormal_points = predict(model=model, df=feature)
    # if abnormal_points['abnormal_score'].item() == 1: # 1: normal, 0: abnormal
    print("Incident !!!")

    add_label = visualize(predictions=abnormal_points, df=feature, cols=list(feature.columns))

    add_label = add_label[add_label['abnormal_score'] == 1]
    arr = add_label.drop(['abnormal_score'], axis=1).to_numpy()
    t = top_map(model=model, k=100000, arr=arr)
    name_mapping = map_feature_name(d=t[0], feature_index=feature_idx)
    # print(name_mapping)
    # name_mapping = dict(list(name_mapping.items())[0: 5]) # take 5 
    # add_weight = compensation(ab_score=name_mapping, topk=5)
    # print(add_weight)
    # print("==========SERVING FINISHED==========")

    rca_mess = {
        "time": time.strftime('%X %x %Z'),
        "status": "Incident",
        # "objects": message(name_mapping),
        # "kind": "net",
        "potential_root_cause": name_mapping
    }
    return rca_mess
    # rca_mess = json.dumps(rca_mess, indent=4)
    # print(json_response)
    # response = send_request("http://127.0.0.1:5000/manager/RCAs", rca_mess)
    # print(response)
    # print(rca_mess)
        
    # else:
    #     print(time.strftime('%X %x %Z') + ": Normal")




"""
def serving_rca(model, feature: pd.DataFrame):
    data_df = pd.DataFrame([feature])
    data_df = data_df.reindex(columns=sorted(data_df.columns))
    print(data_df)
    
    feature = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label'])].copy()
    feature = tp_preprocess_data(df=feature)

    abnormal_points = predict(model=model, df=feature)
    if abnormal_points['abnormal_score'].item() == 1: # 1: normal, 0: abnormal
        print("Incident !!!")
    
        add_label = visualize(predictions=abnormal_points, df=feature, cols=list(feature.columns))

        add_label = add_label[add_label['abnormal_score'] == 1]
        arr = add_label.drop(['abnormal_score'], axis=1).to_numpy()
        t = top_map(model=model, k=100000, arr=arr)
        name_mapping = map_feature_name(t[0])
        # print(name_mapping)
        # name_mapping = dict(list(name_mapping.items())[0: 5]) # take 5 
        # add_weight = compensation(ab_score=name_mapping, topk=5)
        # print(add_weight)
        # print("==========SERVING FINISHED==========")

        rca_mess = {
            "time": time.strftime('%X %x %Z'),
            "status": "Incident",
            "objects": message(name_mapping),
            "kind": "net",
            "potential_root_cause": name_mapping
        }
        rca_mess = json.dumps(rca_mess, indent=4)
        # print(json_response)
        # response = send_request("http://127.0.0.1:5000/manager/RCAs", rca_mess)
        # print(response)
        print(rca_mess)
        
    else:
        print(time.strftime('%X %x %Z') + ": Normal")

"""



