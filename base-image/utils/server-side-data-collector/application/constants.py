# Graph constants
FIGURE_DIMENSIONS = (25, 15)
FONT_SCALE = 1.3

# Table Index
MEMORY_TABLE_INDEX = 0
CPU_TABLE_INDEX = 1

# Dataframe Structure based constants
TIMEGENERATED_COLUMN_INDEX = 0
REQUEST_COLUMN_INDEX = 1
LIMIT_COLUMN_INDEX = 2
POD_DATA_COLUMNS_START_INDEX = 3
COMMON_COLUMNS = [REQUEST_COLUMN_INDEX, LIMIT_COLUMN_INDEX]

# Auth constants
LOGIN_BASE_URL = "https://login.microsoftonline.com"
# [Bandit Suppression] B105: Not a password. This is an endpoint
TOKEN_ENDPOINT = "/oauth2/token"  # nosec B105

# Log analytics constants
LOG_ANALYTICS_API_URL = "https://api.loganalytics.io"
WORKSPACES_ENDPOINT = "/v1/workspaces"
QUERY_ENDPOINT = "/query"

# Kusto sub-query to retrieve memory and CPU
CPU_MEMORY_RETRIVAL_QUERY = """let PerfData = materialize(Perf
| where TimeGenerated >= startDateTime and TimeGenerated < endDateTime + 1m
| where ObjectName == 'K8SContainer'
| join kind = inner (ContainerNames) on $left.InstanceName == $right.ContainerFQN);
PerfData
| where CounterName == 'memoryLimitBytes' or CounterName == 'memoryRequestBytes' or CounterName == 'memoryWorkingSetBytes' or CounterName == 'memoryRssBytes'
| project TimeGenerated, PodName, CounterName, CounterValue = CounterValue / (1024 * 1024)
| make-series Measure=avg(CounterValue) default=0 on TimeGenerated in range(startDateTime, endDateTime, 1m) by PodName, CounterName;
PerfData
| where CounterName == 'cpuLimitNanoCores' or CounterName == 'cpuRequestNanoCores' or CounterName == 'cpuUsageNanoCores'
| project TimeGenerated, PodName, CounterName, CounterValue = CounterValue / (1000 * 1000)
| make-series Measure=avg(CounterValue) default=0 on TimeGenerated in range(startDateTime, endDateTime, 1m) by PodName, CounterName;
"""

SYSTEM_APP_QUERY_TEMPLATE = """
let subscriptionId = '{subscription_id}';
let resourceGroup = '{resource_group}';
let clusterName = '{cluster_name}';
let startDateTime = todatetime('{start_date_time}');
let endDateTime = todatetime('{end_date_time}') + 2m;
let k8sNamespace = '{k8s_namespace}';
let choreoComponent = '{choreo_component}';
let k8sClusterId = strcat('/subscriptions/', subscriptionId, '/resourceGroups/', resourceGroup, '/providers/Microsoft.ContainerService/managedClusters/', clusterName);
let ContainerNames = KubePodInventory
| where TimeGenerated >= startDateTime and TimeGenerated < endDateTime
| where ClusterId == k8sClusterId
| where Namespace == k8sNamespace
| where extractjson("$.[0].['app']", PodLabel) == choreoComponent
| where ContainerName !contains 'linkerd'
| project ContainerFQN = strcat(k8sClusterId, '/', ContainerName), ContainerName, PodName = Name
| distinct ContainerFQN, ContainerName, PodName;
"""

USER_APP_QUERY_TEMPLATE = """
let subscriptionId = '{subscription_id}';
let resourceGroup = '{resource_group}';
let clusterName = '{cluster_name}';
let startDateTime = todatetime('{start_date_time}');
let endDateTime = todatetime('{end_date_time}') + 2m;
let k8sNamespace = '{k8s_namespace}';
let appName = '{app_name}';
let k8sClusterId = strcat('/subscriptions/', subscriptionId, '/resourceGroups/', resourceGroup, '/providers/Microsoft.ContainerService/managedClusters/', clusterName);
let ContainerNames = KubePodInventory
| where TimeGenerated >= startDateTime and TimeGenerated < endDateTime
| where ClusterId == k8sClusterId
| where Namespace == k8sNamespace
| where extractjson('$.[0].app', PodLabel) == appName
| project ContainerFQN = strcat(k8sClusterId, '/', ContainerName), ContainerName, PodName = Name
| distinct ContainerFQN, ContainerName, PodName;
"""
