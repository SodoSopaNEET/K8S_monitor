# Kubernetes Node and Pod Resource Monitor

## Overview

`k8s_monitor.py` 是一個 Python 腳本，用於監控 Kubernetes 節點和待處理 pod 的資源使用情況。它會獲取 CPU 和記憶體使用情況、可分配資源，並計算每個節點的剩餘資源。腳本還會收集待處理 pod 的資源請求。

## Features

- 使用 `kubectl` 獲取每個節點的即時 CPU 和記憶體使用情況。
- 獲取集群中每個節點的可分配資源和標籤。
- 計算每個節點剩餘的 CPU 和記憶體資源。
- 列出待處理的 pod 及其請求的 CPU 和記憶體資源。
- 將節點和待處理 pod 的數據保存為 JSON 格式（`node_resources.json` 和 `pending_pod_resources.json`）。

## Prerequisites

- Python 3.x
- 已配置並可訪問的 Kubernetes 集群
- 安裝並配置好的 `kubectl` 命令行工具
- Python 庫：`kubernetes`, `pandas`

要安裝所需的庫，請執行：

```
pip install kubernetes pandas
```
## 使用 Cron 自動執行腳本

可以使用 cron 來每隔五分鐘自動執行此腳本
在編輯器中新增以下一行：
```
*/5 * * * * /usr/bin/python3 /path/to/k8s_monitor.py
```

## Notes
- 腳本使用 kubectl top nodes 來收集即時資源使用情況，因此 Kubernetes metrics server 必須在集群中運行。沒有此服務，腳本將無法獲取即時 CPU 和記憶體的使用數據。
- 腳本假設 CPU 單位為 millicores (m)，記憶體單位為 KiB 或 MiB。
