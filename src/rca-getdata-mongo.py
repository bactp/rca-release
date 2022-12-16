import pymongo
import requests
import time
import pandas as pd


def db_connection():
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
            metrics.append(0)
        
        
    return metrics

def merge_data(instance_list, data_collection_name):
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

    mydb = db_connection()
    mycon = mydb[data_collection_name]
    info = mycon.insert_one(data)
    print(info.inserted_id, "collect metrics successfully!")


if __name__ == "__main__":

    instance_list = get_instances_list()
    data_collection_name = "training_data_8"
    while True:
        merge_data(instance_list, data_collection_name)
        time.sleep(5)
    #---------
    
