import pymongo
import requests
import schedule
import time
import threading
import pandas as pd
    
def db_connection():
    request_url = "mongodb://bactp:lovedcn123@192.168.40.246:27017/admin"
    db_name = "RCA"
    myclient = pymongo.MongoClient(request_url)
    mydb = myclient[db_name]
    return mydb

def get_host_metrics(compute_3, compute_4):
    compute_3_ip = compute_3['IP_add'] #'192.168.40.244:9090'
    compute_4_ip = compute_4['IP_add']  #'192.168.24.245:9090'
    host_metrics = {
                    'starlab-compute03_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + compute_3_ip +'"}[1m])) * 100)',
                    'starlab-compute03_load_average': 'sum(node_load5{instance="' + compute_3_ip + '"}) / count(node_cpu_seconds_total{mode="system",instance="' + compute_3_ip + '"})*100',
                    'starlab-compute03_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + compute_3_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + compute_3_ip + '"})*100)',
                    'starlab-compute03_disk_utilization': '(sum(node_filesystem_size_bytes{instance="' + compute_3_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + compute_3_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + compute_3_ip + '"})*100',
                    'starlab-compute03_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + compute_3_ip + '"}[1m]))/1024',
                    'starlab-compute03_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + compute_3_ip + '"}[1m]))/1024',
                    'starlab-compute03_net_rx_eno1': 'sum(rate(node_network_receive_bytes_total{instance="' + compute_3_ip + '", device="eno1"}[1m]))/1024',
                    'starlab-compute03_net_tx_eno1': 'sum(rate(node_network_transmit_bytes_total{instance="' + compute_3_ip + '", device="eno1"}[1m]))/1024',
                    'starlab-compute03_net_rx_drop_eno1': 'sum(rate(node_network_receive_drop_total{instance="' + compute_3_ip + '", device="eno1"}[1m]))',
                    'starlab-compute03_net_tx_drop_eno1': 'sum(rate(node_network_transmit_drop_total{instance="' + compute_3_ip + '", device="eno1"}[1m]))',
                    'starlab-compute03_net_rx_err_eno1': 'sum(rate(node_network_receive_errs_total{instance="' + compute_3_ip + '", device="eno1"}[1m]))',
                    'starlab-compute03_net_tx_err_eno1': 'sum(rate(node_network_transmit_errs_total{instance="' + compute_3_ip + '", device="eno1"}[1m]))',
                    'starlab-compute03_net_rx_eno2': 'sum(rate(node_network_receive_bytes_total{instance="' + compute_3_ip + '", device="eno2"}[1m]))/1024',
                    'starlab-compute03_net_tx_eno2': 'sum(rate(node_network_transmit_bytes_total{instance="' + compute_3_ip + '", device="eno2"}[1m]))/1024',
                    'starlab-compute03_net_rx_drop_eno2': 'sum(rate(node_network_receive_drop_total{instance="' + compute_3_ip + '", device="eno2"}[1m]))',
                    'starlab-compute03_net_tx_drop_eno2': 'sum(rate(node_network_transmit_drop_total{instance="' + compute_3_ip + '", device="eno2"}[1m]))',
                    'starlab-compute03_net_rx_err_eno2': 'sum(rate(node_network_receive_errs_total{instance="' + compute_3_ip + '", device="eno2"}[1m]))',
                    'starlab-compute03_net_tx_err_eno2': 'sum(rate(node_network_transmit_errs_total{instance="' + compute_3_ip + '", device="eno2"}[1m]))',
                    'starlab-compute03_temp_cel': 'avg(node_hwmon_temp_celsius{instance="' + compute_3_ip + '"})',     
                    'starlab-compute04_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + compute_4_ip + '"}[1m])) * 100)',
                    'starlab-compute04_load_average': 'sum(node_load5{instance="' + compute_4_ip + '"}) / count(node_cpu_seconds_total{mode="system",instance="' + compute_4_ip + '"})*100',
                    'starlab-compute04_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + compute_4_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + compute_4_ip + '"})*100)',
                    'starlab-compute04_disk_utilization': '(sum(node_filesystem_size_bytes{instance="' + compute_4_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + compute_4_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + compute_4_ip + '"})*100',
                    'starlab-compute04_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + compute_4_ip + '"}[1m]))/1024',
                    'starlab-compute04_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + compute_4_ip + '"}[1m]))/1024',
                    'starlab-compute04_net_rx_eno1': 'sum(rate(node_network_receive_bytes_total{instance="' + compute_4_ip + '", device="eno1"}[1m]))/1024',
                    'starlab-compute04_net_tx_eno1': 'sum(rate(node_network_transmit_bytes_total{instance="' + compute_4_ip + '", device="eno1"}[1m]))/1024',
                    'starlab-compute04_net_rx_drop_eno1': 'sum(rate(node_network_receive_drop_total{instance="' + compute_4_ip + '", device="eno1"}[1m]))',
                    'starlab-compute04_net_tx_drop_eno1': 'sum(rate(node_network_transmit_drop_total{instance="' + compute_4_ip + '", device="eno1"}[1m]))',
                    'starlab-compute04_net_rx_err_eno1': 'sum(rate(node_network_receive_errs_total{instance="' + compute_4_ip + '", device="eno1"}[1m]))',
                    'starlab-compute04_net_tx_err_eno1': 'sum(rate(node_network_transmit_errs_total{instance="' + compute_4_ip + '", device="eno1"}[1m]))',
                    'starlab-compute04_net_rx_eno2': 'sum(rate(node_network_receive_bytes_total{instance="' + compute_4_ip + '", device="eno2"}[1m]))/1024',
                    'starlab-compute04_net_tx_eno2': 'sum(rate(node_network_transmit_bytes_total{instance="' + compute_4_ip + '", device="eno2"}[1m]))/1024',
                    'starlab-compute04_net_rx_drop_eno2': 'sum(rate(node_network_receive_drop_total{instance="' + compute_4_ip + '", device="eno2"}[1m]))',
                    'starlab-compute04_net_tx_drop_eno2': 'sum(rate(node_network_transmit_drop_total{instance="' + compute_4_ip + '", device="eno2"}[1m]))',
                    'starlab-compute04_net_rx_err_eno2': 'sum(rate(node_network_receive_errs_total{instance="' + compute_4_ip + '", device="eno2"}[1m]))',
                    'starlab-compute04_net_tx_err_eno2': 'sum(rate(node_network_transmit_errs_total{instance="' + compute_4_ip + '", device="eno2"}[1m]))',
                    'starlab-compute04_temp_cel': 'avg(node_hwmon_temp_celsius{instance="' + compute_4_ip + '"})',
                    } 

    values = []
    for metric_name, metric_value in host_metrics.items():
        #print(metric_value)
        try:
            response = requests.get('http://192.168.40.232:31270/api/v1/query', params={'query': metric_value})
            if bool(response.json()['data']['result']):
                host = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                values.append(host)
            else:
                values.append(0)
        except:
            values.append(0)
        
    print()
    return values


a = "count(node_cpu_seconds_total) by (exported_instance)"
def get_vm_metrics_new():
    values = []
    try:
        response = requests.get('http://192.168.40.232:31270/api/v1/query', params={'query': "machine_types"})
        if bool(response.json()['data']['result']):
            host = response.json()['data']['result']
            values.append(host)
    except:
        values.append(0)



    vm_metrics =  {
                    'hyungnam-worker1_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + hyungnam_worker1_ip + '"}[1m])) * 100)',
                    'hyungnam-worker1_load_average': 'sum(node_load5{instance="' + hyungnam_worker1_ip + '"}) / count(node_cpu_seconds_total{instance="' + hyungnam_worker1_ip + '", mode="system"})*100',
                    'hyungnam-worker1_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + hyungnam_worker1_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + hyungnam_worker1_ip + '"})*100)',
                    'hyungnam-worker1_disk_utilization': '(sum(node_filesystem_size_bytes{instance="' + hyungnam_worker1_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + hyungnam_worker1_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + hyungnam_worker1_ip + '"})*100',
                    'hyungnam-worker1_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + hyungnam_worker1_ip + '"}[1m]))/1024',
                    'hyungnam-worker1_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + hyungnam_worker1_ip + '"}[1m]))/1024',
                    'hyungnam-worker1_net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker1_net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker1_net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker1_net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker1_net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker1_net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + hyungnam_worker2_ip + '"}[1m])) * 100)',
                    'hyungnam-worker2_load_average': 'sum(node_load5{instance="' + hyungnam_worker2_ip + '"}) / count(node_cpu_seconds_total{instance="' + hyungnam_worker2_ip + '", mode="system"})*100',
                    'hyungnam-worker2_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + hyungnam_worker2_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + hyungnam_worker2_ip + '"})*100)',
                    'hyungnam-worker2_disk_utilaization': '(sum(node_filesystem_size_bytes{instance="' + hyungnam_worker2_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + hyungnam_worker2_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + hyungnam_worker2_ip + '"})*100',
                    'hyungnam-worker2_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + hyungnam_worker2_ip + '"}[1m]))/1024',
                    'hyungnam-worker2_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + hyungnam_worker2_ip + '"}[1m]))/1024',
                    'hyungnam-worker2_net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker2_net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker2_net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + hyungnam_worker3_ip + '"}[1m])) * 100)',
                    'hyungnam-worker3_load_average': 'sum(node_load5{instance="' + hyungnam_worker3_ip + '"}) / count(node_cpu_seconds_total{instance="' + hyungnam_worker3_ip + '", mode="system"})*100',
                    'hyungnam-worker3_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + hyungnam_worker3_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + hyungnam_worker3_ip + '"})*100)',
                    'hyungnam-worker3_disk_utilaization': '(sum(node_filesystem_size_bytes{instance="' + hyungnam_worker3_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + hyungnam_worker3_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + hyungnam_worker3_ip + '"})*100',
                    'hyungnam-worker3_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + hyungnam_worker3_ip + '"}[1m]))/1024',
                    'hyungnam-worker3_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + hyungnam_worker3_ip + '"}[1m]))/1024',
                    'hyungnam-worker3_net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker3_net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker3_net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    }
    
   
        
    return values





def get_vm_metrics(hyungnam_worker1, hyungnam_worker2, hyungnam_worker3):
    hyungnam_worker1_ip = hyungnam_worker1['IP_add'] #',10.244.1.14:9100,
    hyungnam_worker2_ip = hyungnam_worker2['IP_add']  #'10.244.2.25:9100
    hyungnam_worker3_ip = hyungnam_worker3['IP_add']  #'10.244.3.2:9100
    vm_metrics =  {
                    'hyungnam-worker1_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + hyungnam_worker1_ip + '"}[1m])) * 100)',
                    'hyungnam-worker1_load_average': 'sum(node_load5{instance="' + hyungnam_worker1_ip + '"}) / count(node_cpu_seconds_total{instance="' + hyungnam_worker1_ip + '", mode="system"})*100',
                    'hyungnam-worker1_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + hyungnam_worker1_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + hyungnam_worker1_ip + '"})*100)',
                    'hyungnam-worker1_disk_utilization': '(sum(node_filesystem_size_bytes{instance="' + hyungnam_worker1_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + hyungnam_worker1_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + hyungnam_worker1_ip + '"})*100',
                    'hyungnam-worker1_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + hyungnam_worker1_ip + '"}[1m]))/1024',
                    'hyungnam-worker1_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + hyungnam_worker1_ip + '"}[1m]))/1024',
                    'hyungnam-worker1_net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker1_net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker1_net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker1_net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker1_net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker1_net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + hyungnam_worker1_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + hyungnam_worker2_ip + '"}[1m])) * 100)',
                    'hyungnam-worker2_load_average': 'sum(node_load5{instance="' + hyungnam_worker2_ip + '"}) / count(node_cpu_seconds_total{instance="' + hyungnam_worker2_ip + '", mode="system"})*100',
                    'hyungnam-worker2_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + hyungnam_worker2_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + hyungnam_worker2_ip + '"})*100)',
                    'hyungnam-worker2_disk_utilaization': '(sum(node_filesystem_size_bytes{instance="' + hyungnam_worker2_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + hyungnam_worker2_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + hyungnam_worker2_ip + '"})*100',
                    'hyungnam-worker2_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + hyungnam_worker2_ip + '"}[1m]))/1024',
                    'hyungnam-worker2_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + hyungnam_worker2_ip + '"}[1m]))/1024',
                    'hyungnam-worker2_net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker2_net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker2_net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker2_net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + hyungnam_worker2_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="' + hyungnam_worker3_ip + '"}[1m])) * 100)',
                    'hyungnam-worker3_load_average': 'sum(node_load5{instance="' + hyungnam_worker3_ip + '"}) / count(node_cpu_seconds_total{instance="' + hyungnam_worker3_ip + '", mode="system"})*100',
                    'hyungnam-worker3_mem_utilization': '100 - (sum(node_memory_MemAvailable_bytes{instance="' + hyungnam_worker3_ip + '"}) / sum(node_memory_MemTotal_bytes{instance="' + hyungnam_worker3_ip + '"})*100)',
                    'hyungnam-worker3_disk_utilaization': '(sum(node_filesystem_size_bytes{instance="' + hyungnam_worker3_ip + '"}) - sum(node_filesystem_free_bytes{instance="' + hyungnam_worker3_ip + '"})) / sum(node_filesystem_size_bytes{instance="' + hyungnam_worker3_ip + '"})*100',
                    'hyungnam-worker3_disk_read': 'sum(rate(node_disk_read_bytes_total{instance="' + hyungnam_worker3_ip + '"}[1m]))/1024',
                    'hyungnam-worker3_disk_write': 'sum(rate(node_disk_written_bytes_total{instance="' + hyungnam_worker3_ip + '"}[1m]))/1024',
                    'hyungnam-worker3_net_rx': 'sum(rate(node_network_receive_bytes_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker3_net_tx': 'sum(rate(node_network_transmit_bytes_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))/1024',
                    'hyungnam-worker3_net_rx_drop': 'sum(rate(node_network_receive_drop_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_net_tx_drop': 'sum(rate(node_network_transmit_drop_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_net_rx_err': 'sum(rate(node_network_receive_errs_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    'hyungnam-worker3_net_tx_err': 'sum(rate(node_network_transmit_errs_total{instance="' + hyungnam_worker3_ip + '", device="eth0"}[1m]))',
                    }
    
    values = []
    for metric_name, metric_value in vm_metrics.items():
        try:
            response = requests.get('http://192.168.40.144:30000//api/v1/query', params={'query': metric_value})
            if bool(response.json()['data']['result']):
                vm = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                values.append(vm)
            else:
                values.append(0)
        except:
            values.append(0)
        
    return values

def get_app_metrics():
    app_metrics = {
                        'request_per_second': 'round(sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"sock-shop",destination_workload=~"front-end"}[1m])), 0.001)',
                        'incoming_success_rate': 'sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"sock-shop",destination_workload=~"front-end",response_code!~"5.*"}[1m])) / sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"sock-shop",destination_workload=~"front-end"}[1m]))',
                        'latency': '(histogram_quantile(0.90, sum(irate(istio_request_duration_milliseconds_bucket{reporter=~"destination",destination_workload=~"front-end", destination_workload_namespace=~"sock-shop"}[1m])) by (le)) / 1000) or histogram_quantile(0.90, sum(irate(istio_request_duration_seconds_bucket{reporter=~"destination",destination_workload=~"front-end", destination_workload_namespace=~"sock-shop"}[1m])) by (le))',
                        }
    values = []
    for metric_name, metric_value in app_metrics.items():
        try:
            response = requests.get('http://192.168.40.144:30000/api/v1/query', params={'query': metric_value})
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                values.append(test)
            else:
                values.append(0)
        except:
            values.append(0)
        
    return values


def get_container_metrics(name):
    container_metrics = {
                        'cpu_cfs_periods_total': 'avg(rate(container_cpu_cfs_periods_total{namespace="sock-shop", container="' + name +'"}[1m]))',
                        'cpu_cfs_throttled': 'avg(rate(container_cpu_cfs_throttled_periods_total{namespace="sock-shop", container="' + name + '"}[1m]))',
                        'cpu_usage': '(avg(rate(container_cpu_usage_seconds_total{namespace="sock-shop", container="' + name +'"}[1m]))) / (sum(kube_pod_container_resource_limits{namespace="sock-shop", container="' + name +'", resource="cpu"}))*100',
                        'mem_usage': '(avg(rate(container_memory_usage_bytes{namespace="sock-shop", container="' + name +'"}[1m]))) / sum(kube_pod_container_resource_limits{namespace="sock-shop", container="' + name +'", resource="memory"})*100',
                        'net_rx_byte': 'avg(rate(container_network_receive_bytes_total{namespace="sock-shop", pod=~"' + name +'.*", pod!~"' + name +'-db.*"}[1m]))/1024',
                        'net_tx_byte': 'avg(rate(container_network_transmit_bytes_total{namespace="sock-shop", pod=~"' + name +'.*", pod!~"' + name +'-db.*"}[1m]))/1024',
                        'net_rx_drop': 'avg(rate(container_network_receive_packets_dropped_total{namespace="sock-shop", pod=~"' + name +'.*", pod!~"' + name +'-db.*"}[1m]))',
                        'net_tx_drop': 'avg(rate(container_network_transmit_packets_dropped_total{namespace="sock-shop", pod=~"' + name +'.*", pod!~"' + name +'-db.*"}[1m]))',
                        'net_rx_error': 'avg(rate(container_network_receive_errors_total{namespace="sock-shop", pod=~"' + name +'.*", pod!~"' + name +'-db.*"}[1m]))',
                        'net_tx_error': 'avg(rate(container_network_transmit_errors_total{namespace="sock-shop", pod=~"' + name +'.*", pod!~"' + name +'-db.*"}[1m]))'
                        }
    metrics = []
    for metric_name, metric_value in container_metrics.items():
        try:
            response = requests.get('http://192.168.40.144:30000/api/v1/query', params={'query': metric_value})
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                metrics.append(test)
            else:
                metrics.append(0)
        except:
            metrics.append(0)
        
        
    return metrics



def merge_data_save(compute_3, compute_4, hyungnam_worker1, hyungnam_worker2, hyungnam_worker3):
    data = {}
    compute_metrics = get_host_metrics(compute_3, compute_4)
    data.update({
                "starlab-compute03_CPU_utilization":   compute_metrics[0],
                "starlab-compute03_load_average":   compute_metrics[1],
                "starlab-compute03_mem_utilization":   compute_metrics[2],
                "starlab-compute03_disk_utilization":   compute_metrics[3],
                "starlab-compute03_disk_read":   compute_metrics[4],
                "starlab-compute03_disk_write":   compute_metrics[5],
                "starlab-compute03_net_rx_eno1":   compute_metrics[6],
                "starlab-compute03_net_tx_eno1":   compute_metrics[7],
                "starlab-compute03_net_rx_drop_eno1":   compute_metrics[8],
                "starlab-compute03_net_tx_drop_eno1":   compute_metrics[9],
                "starlab-compute03_net_rx_err_eno1":   compute_metrics[10],
                "starlab-compute03_net_tx_err_eno1":   compute_metrics[11],
                "starlab-compute03_net_rx_eno2":   compute_metrics[12],
                "starlab-compute03_net_tx_eno2":   compute_metrics[13],
                "starlab-compute03_net_rx_drop_eno2":   compute_metrics[14],
                "starlab-compute03_net_tx_drop_eno2":   compute_metrics[15],
                "starlab-compute03_net_rx_err_eno2":   compute_metrics[16],
                "starlab-compute03_net_tx_err_eno2":   compute_metrics[17],
                "starlab-compute03_temp_cel":   compute_metrics[18],
                "starlab-compute04_CPU_utilization":   compute_metrics[19],
                "starlab-compute04_load_average":   compute_metrics[20],
                "starlab-compute04_mem_utilization":   compute_metrics[21],
                "starlab-compute04_disk_utilization":   compute_metrics[22],
                "starlab-compute04_disk_read":   compute_metrics[23],
                "starlab-compute04_disk_write":   compute_metrics[24],
                "starlab-compute04_net_rx_eno1":   compute_metrics[25],
                "starlab-compute04_net_tx_eno1":   compute_metrics[26],
                "starlab-compute04_net_rx_drop_eno1":   compute_metrics[27],
                "starlab-compute04_net_tx_drop_eno1":   compute_metrics[28],
                "starlab-compute04_net_rx_err_eno1":   compute_metrics[29],
                "starlab-compute04_net_tx_err_eno1":   compute_metrics[30],
                "starlab-compute04_net_rx_eno2":   compute_metrics[31],
                "starlab-compute04_net_tx_eno2":   compute_metrics[32],
                "starlab-compute04_net_rx_drop_eno2":   compute_metrics[33],
                "starlab-compute04_net_tx_drop_eno2":   compute_metrics[34],
                "starlab-compute04_net_rx_err_eno2":   compute_metrics[35],
                "starlab-compute04_net_tx_err_eno2":   compute_metrics[36],
                "starlab-compute04_temp_cel":   compute_metrics[37],
               })
    print("==========HOST METRICS COLLECTED==========")

    vm_metrics = get_vm_metrics(hyungnam_worker1, hyungnam_worker2, hyungnam_worker3)
    data.update({
                "hyungnam-worker1_CPU_utilization":  vm_metrics[0],
                "hyungnam-worker1_load_average":  vm_metrics[1],
                "hyungnam-worker1_mem_utilization":  vm_metrics[2],
                "hyungnam-worker1_disk_utilization":  vm_metrics[3],
                "hyungnam-worker1_disk_read":  vm_metrics[4],
                "hyungnam-worker1_disk_write":  vm_metrics[5],
                "hyungnam-worker1_net_rx":  vm_metrics[6],
                "hyungnam-worker1_net_tx":  vm_metrics[7],
                "hyungnam-worker1_net_rx_drop":  vm_metrics[8],
                "hyungnam-worker1_net_tx_drop":  vm_metrics[9],
                "hyungnam-worker1_net_rx_err":  vm_metrics[10],
                "hyungnam-worker1_net_tx_err":  vm_metrics[11],
                "hyungnam-worker2_CPU_utilization":  vm_metrics[12],
                "hyungnam-worker2_load_average":  vm_metrics[13],
                "hyungnam-worker2_mem_utilization":  vm_metrics[14],
                "hyungnam-worker2_disk_utilaization":  vm_metrics[15],
                "hyungnam-worker2_disk_read":  vm_metrics[16],
                "hyungnam-worker2_disk_write":  vm_metrics[17],
                "hyungnam-worker2_net_rx":  vm_metrics[18],
                "hyungnam-worker2_net_tx":  vm_metrics[19],
                "hyungnam-worker2_net_rx_drop":  vm_metrics[20],
                "hyungnam-worker2_net_tx_drop":  vm_metrics[21],
                "hyungnam-worker2_net_rx_err":  vm_metrics[22],
                "hyungnam-worker2_net_tx_err":  vm_metrics[23],
                "hyungnam-worker3_CPU_utilization":  vm_metrics[24],
                "hyungnam-worker3_load_average":  vm_metrics[25],
                "hyungnam-worker3_mem_utilization":  vm_metrics[26],
                "hyungnam-worker3_disk_utilaization":  vm_metrics[27],
                "hyungnam-worker3_disk_read":  vm_metrics[28],
                "hyungnam-worker3_disk_write":  vm_metrics[29],
                "hyungnam-worker3_net_rx":  vm_metrics[30],
                "hyungnam-worker3_net_tx":  vm_metrics[31],
                "hyungnam-worker3_net_rx_drop":  vm_metrics[32],
                "hyungnam-worker3_net_tx_drop":  vm_metrics[33],
                "hyungnam-worker3_net_rx_err":  vm_metrics[34],
                "hyungnam-worker3_net_tx_err":  vm_metrics[35],
                })
    print("==========VM METRICS COLLECTED==========")

    app_metrics = get_app_metrics()
    data.update({
                'request_per_second': app_metrics[0],
                'incoming_success_rate': app_metrics[1],
                'latency': app_metrics[2],
                })
    print("=========APP METRICS COLLECTED==========")

    container_name = {"catalogue", "front-end", "orders", "payment", "queue-master", "shipping"}
    for name in container_name:
        container_metrics = get_container_metrics(name)

        data.update({
                    name + '_cpu_cfs_periods_total': container_metrics[0],
                    name + '_cpu_cfs_throttled': container_metrics[1],
                    name + '_cpu_usage': container_metrics[2],
                    name + '_mem_usage': container_metrics[3],
                    name + '_net_rx_byte': container_metrics[4],
                    name + '_net_tx_byte': container_metrics[5],
                    name + '_net_rx_drop': container_metrics[6],
                    name + '_net_tx_drop': container_metrics[7],
                    name + '_net_rx_error': container_metrics[8],
                    name + '_net_tx_error': container_metrics[9]
                    })
    
    print("==========APP METRICS COLLECTED==========")
    
    data.update({
                 'timestamp': time.strftime('%X %x %Z')
                })

    mydb = db_connection()
    mycon = mydb["training_data5"]
    info = mycon.insert_one(data)
    print(info.inserted_id, "collect metrics successfully!")


# name: IP
compute_3 = {
            'IP_add': '192.168.40.244:9100',
            'Name': 'compute_node_3',
            }
compute_4 = {
            'IP_add': '192.168.40.245:9100',
            'Name': 'compute_node_4',
            }
hyungnam_worker1 = {
        'IP_add': '10.244.1.14:9100',
        'Name': 'vm_1',
        }
hyungnam_worker2 = {
        'IP_add': '10.244.2.25:9100',
        'Name': 'vm_2',
        }
hyungnam_worker3 = {
        'IP_add': '10.244.3.2:9100',
        'Name': 'vm_3',
        }

# label = '0' #0-normal, 1-abnormal
# t1 = threading.Thread(target=schedule.every(10).seconds.do(merge_data_save, compute_3, compute_4, hyungnam_worker1, hyungnam_worker2, hyungnam_worker3), args=(10,))

# while True:
#     schedule.run_pending()
#     time.sleep(1)

while True:
    merge_data_save(compute_3, compute_4, hyungnam_worker1, hyungnam_worker2, hyungnam_worker3)
    time.sleep(10)
