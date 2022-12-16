import pymongo
import requests
import time
import pandas as pd
from minio import Minio
from minio.error import S3Error
from sys import getsizeof
import json
import io

def db_connection():
    request_url = "mongodb://bactp:lovedcn123@192.168.40.246:27017/admin"
    db_name = "RCA"
    myclient = pymongo.MongoClient(request_url)
    mydb = myclient[db_name]
    return mydb

# Init parameter to create minio client
def init_minio_connect():
    client = Minio(
        "192.168.40.232:32060",
        access_key="IOfOcEOJ7oCsUaLF",
        secret_key="vNjq6bdPdnOYoJJZ15y5AnKcTHqF3N2O",
        secure=False,)
    return client

# Create bucket Minio with client and bucket name
def create_bucket_mino(client, bucket_name):
    print("Creating bucket minio: "+ bucket_name)
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
    else:
        print("Bucket %s already exists", bucket_name)
# Upload file function to minio bucket
def upload_file_to_minio_bucket(client, bucket_name, file_path, object_name, file_type="application/binary"):
    result = client.fput_object(bucket_name, object_name, file_path, content_type= file_type)
    print(
        "created {0} object; etag: {1}, version-id: {2}".format(
            result.object_name, result.etag, result.version_id,
        ),
    )
def stream_upload_object_to_mino_bucket(client, bucket_name, data, object_name):
    buf = io.BytesIO(json.dumps(data).encode())
    length = buf.getbuffer().nbytes
    print("Uploading object....", object_name)
    result = client.put_object(bucket_name, object_name, buf , length,
                                content_type="application/octet-stream", metadata=None, sse=None,
                                progress=None, part_size=0, num_parallel_uploads=3,
                                tags=None, retention=None, legal_hold=False)
    print(
        "created {0} object; etag: {1}, version-id: {2}".format(
            result.object_name, result.etag, result.version_id,
        ),
    )
def list_object_minio(client, bucket_name, path=None):
    print("Getting list object....")
    objects = client.list_objects(bucket_name, path, 
                        recursive=False, start_after=None,
                        include_user_meta=False, include_version=False,
                        use_api_v1=False, use_url_encoding_type=True)
    print("Printting stat object from bucket...")
    # Get object information.
    for obj in objects:
        print(str(obj))
        # object_name = obj
        # result = client.stat_object(bucket_name, object_name)
        # print(
        #     "last-modified: {0}, size: {1}".format(
        #         result.last_modified, result.size,
        #     ),
        # )
    return objects
def read_minio_object(client, bucket_name, object_name, path=None):

    client.get_object(bucket_name, object_name, 
                    offset=0, length=0, request_headers=None,
                    ssec=None, version_id=None, extra_query_params=None)
    
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

    # mydb = db_connection()
    # mycon = mydb["training_data5"]
    # info = mycon.insert_one(data)
    # print(info.inserted_id, "collect metrics successfully!")
    print(data)


if __name__ == "__main__":

    instance_list = get_instances_list()
    client = init_minio_connect()

    create_bucket_mino(client, "testbucket")
    list_object_minio(client, "testbucket")

    while True:
        temp_merge_data = merge_data(instance_list)
        
        stream_upload_object_to_mino_bucket(client, "testbucket", temp_merge_data, "mergedata-" + str(time.strftime("%m-%d-%Y-%H-%M-%S")))
        time.sleep(5)
    #---------
    
