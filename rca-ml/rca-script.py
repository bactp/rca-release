import requests
import schedule
import time
import threading
import json

def get_vm_metric():
    vm_metrics = { 
                    'VM1_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", node="vm-worker1"}[1m])) * 100)',
                    'VM2_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", node="vm-worker2"}[1m])) * 100)',
                    'VM2_Net_trasmit': 'sum(rate(node_network_transmit_bytes_total{node="vm-worker2", device="ens3"}[1m]))/1024'
                }
    values = []
    # print(metric)
    # print(type(metric))
    for metric_name, metric_value in vm_metrics.items():
        # print('metric')
        try: 
            response = requests.get('http://192.168.24.153:30618/api/v1/query', params={'query': metric_value})
        # print((response.json()))
        
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                
                # print(values)
        except:
            print(" ")
        values.append(test)
    return values

def get_host_metric():
    cn_metrics = {
                    'CN1_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="192.168.24.11:9100"}[1m])) * 100)',
                    'CN2_CPU_utilization': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="192.168.24.12:9100"}[1m])) * 100)',
                }
    values = []
    # print(metric)
    # print(type(metric))
    for metric_name, metric_value in cn_metrics.items():
        try: 
        # print('metric')
            response = requests.get('http://192.168.24.10:9091/api/v1/query', params={'query': metric_value})
        # print((response.json()))
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                
                # print(values)
        except:
            print(" ")
        values.append(test)

    return values

def check_pod_status():
    metrics = 'kube_pod_status_scheduled{namespace="monitoring", pod="demo", condition="false"}'
    try: 
    # print('metric')
        response = requests.get('http://192.168.24.153:31902/api/v1/query', params={'query': metrics})
    # print((response.json()))
        if bool(response.json()['data']['result']):
            test = float(response.json()['data']['result'][0]['value'][1])
            if test == 1:
                message = {"message": {
                            "__name__": "kube_pod_status_scheduled",
                            "condition": "false",
                            "namespace": "monitoring",
                            "pod": "demo",
                            "location": "cluster-1"
                            }
                        }
                print(json.dumps(message, indent = 3))
    except:
        print(" ")


def prediction():
    vm_t1 = get_vm_metric()
    host_t1 = get_host_metric()
    time.sleep(3)
    vm_t2 = get_vm_metric()
    host_t2 = get_host_metric()
    time.sleep(3)
    vm_t3 = get_vm_metric()
    host_t3 = get_host_metric()
   
    vm1 = (vm_t1[0]+ vm_t2[0] + vm_t3[0])/3
    vm2 = (vm_t1[1]+ vm_t2[1] + vm_t3[1])/3
    h1 = (host_t1[0]+ host_t2[0] + host_t3[0])/3
    h2 = (host_t1[1]+ host_t2[1] + host_t3[1])/3
    condition = (vm1 + vm2 )/2

    net2= (vm_t1[2]+ vm_t2[2] + vm_t3[2])/3
    
    if condition > 85:
        message = {"message": {
                        "time": time.strftime('%X %x %Z'),
                        "__prediction__": "INCIDENT",
                        "location": "cluster-1",
                        "possible root cause": "cluster CPU hign ultilization",
                        "compute_node_1_remaining": str( 100 - host_t3[0]),
                        "compute_node_2_remaining": str( 100 - host_t3[1]),
                        }
                    }
        print(json.dumps(message, indent = 3))
    elif net2 < 180:
        message = {"message": {
                        "time": time.strftime('%X %x %Z'),
                        "__prediction__": "INCIDENT",
                        "location": "worker-2",
                        "possible root cause": "network-interface-loss",
                        }
                    }
        print(json.dumps(message, indent = 3))
    else:
        print(time.strftime('%X %x %Z') + ": NORMAL")



t1 = threading.Thread(target=schedule.every(10).seconds.do(prediction), args=(10,))
t2 = threading.Thread(target=schedule.every(10).seconds.do(check_pod_status), args=(10,))


while True:
    schedule.run_pending()
    time.sleep(1)