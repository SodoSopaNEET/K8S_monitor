from kubernetes import client, config
import subprocess
import pandas as pd

def get_node_metrics():
    # Use kubectl top nodes to get current node metrics
    output = subprocess.check_output(["kubectl", "top", "nodes", "--no-headers"])
    lines = output.decode("utf-8").splitlines()
    metrics = {}
    for line in lines:
        parts = line.split()
        node_name = parts[0]

        # Check if CPU and memory usage data are available
        cpu_usage = parts[1][:-1] if len(parts) > 1 and parts[1].endswith('m') else '0'
        memory_usage = parts[2][:-2] if len(parts) > 2 and parts[2].endswith('Mi') else '0'

        metrics[node_name] = {
            'cpu_usage': int(cpu_usage) if cpu_usage.isdigit() else 0,
            'memory_usage': int(memory_usage) if memory_usage.isdigit() else 0
        }
    return metrics

def get_node_resources():
    config.load_kube_config()
    v1 = client.CoreV1Api()

    nodes = v1.list_node()
    node_metrics = get_node_metrics()
    data = []

    for node in nodes.items:
        name = node.metadata.name
        labels = node.metadata.labels
        cpu = node.status.allocatable.get('cpu')
        memory = node.status.allocatable.get('memory')

        # Handle CPU allocation, convert cores or millicores to millicores
        if 'm' in cpu:
            cpu_allocatable = int(cpu[:-1])
        else:
            cpu_allocatable = int(cpu) * 1000  # If in cores, convert to millicores

        # Handle memory allocation, assume unit is 'Ki'
        memory_allocatable = int(memory[:-2]) if memory.endswith('Ki') else int(memory)

        # Get the current usage from the metrics
        cpu_usage = node_metrics.get(name, {}).get('cpu_usage', 0)
        memory_usage = node_metrics.get(name, {}).get('memory_usage', 0)

        # Calculate the remaining resources
        cpu_remaining = cpu_allocatable - cpu_usage
        memory_remaining = memory_allocatable - memory_usage

        data.append({
            "Node": name,
            "CPU Allocatable (m)": cpu_allocatable,
            "Memory Allocatable (Ki)": memory_allocatable,
            "CPU Usage (m)": cpu_usage,
            "Memory Usage (Ki)": memory_usage,
            "CPU Remaining (m)": cpu_remaining,
            "Memory Remaining (Ki)": memory_remaining,
            "Labels": labels
        })

    # Convert to DataFrame
    node_df = pd.DataFrame(data)
    return node_df

def get_pending_pod_resources():
    config.load_kube_config()
    v1 = client.CoreV1Api()

    pods = v1.list_pod_for_all_namespaces(field_selector='status.phase=Pending')
    data = []

    for pod in pods.items:
        name = pod.metadata.name
        namespace = pod.metadata.namespace
        labels = pod.metadata.labels

        pod_cpu_request = 0
        pod_memory_request = 0

        for container in pod.spec.containers:
            resources = container.resources.requests
            if resources:
                cpu_request = resources.get('cpu', '0')
                memory_request = resources.get('memory', '0')

                # Convert CPU to millicores
                if 'm' in cpu_request:
                    pod_cpu_request += int(cpu_request[:-1])
                else:
                    pod_cpu_request += int(cpu_request) * 1000

                # Convert Memory to Mi
                if 'Mi' in memory_request:
                    pod_memory_request += int(memory_request[:-2])
                elif 'Gi' in memory_request:
                    pod_memory_request += int(memory_request[:-2]) * 1024

        data.append({
            "Pod": name,
            "Namespace": namespace,
            "CPU Request (m)": pod_cpu_request,
            "Memory Request (Mi)": pod_memory_request,
            "Labels": labels
        })

    pending_pod_df = pd.DataFrame(data)
    return pending_pod_df

if __name__ == "__main__":
    node_df = get_node_resources()
    pending_pod_df = get_pending_pod_resources()

    node_df.to_json("node_resources.json", orient="records", indent=4)
    print("Node resources saved to node_resources.json")

    pending_pod_df.to_json("pending_pod_resources.json", orient="records", indent=4)
    print("Pending pod resources saved to pending_pod_resources.json")
