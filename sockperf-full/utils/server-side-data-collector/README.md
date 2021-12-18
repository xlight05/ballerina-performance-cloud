# Server-side metric monitor for Choreo
This directory of the Choreo Performance repository contains the codebase for server-side metric monitoring of Choreo performance tests. It collects memory and CPU usage data for system apps and user apps.

## Folders and files

The `application` folder contains the Python code for the `server-monitor` package. The `setup.py` is used for the packaging of the said package. The `system.txt` contains the set of system apps we will collect metrics for. (Please edit this accordingly if needed.) The `runServerMonitor.sh` is used as an entrypoint for running the `server-monitor` in docker.

## Running server-monitor in Docker
```
docker container run \
--workdir /perf-test \
--mount type=bind,source=${PATH_TO_SERVER_SIDE_SCRIPTS},target=/perf-test \
--mount type=bind,source=${PATH_TO_USER_APP_NAMES_FILE},target=/conf/user.txt \
--mount type=bind,source=${ROOT},target=/output \
--rm \
ubuntu:20.04 \
bash -c "apt-get update && apt-get install -y --no-install-recommends python3.9=3.9.0-5~20.04 python3-pip=20.0.2-5ubuntu1.1 && pip3 install -e . && \
bash /perf-test/runServerMonitor.sh /output ${{TEST_NAME}} ${{TENENT_ID}} ${{CLIENT_ID}} ${{CLIENT_SECRET} ${{WORKSPACE_ID}} ${{ORGANIZATION_NAME}} \
/perf-test/system.txt /conf/user.txt ${{START_TIME}} ${{END_TIME}} \
${{SUBSCRIPTION_ID_SYSTEM}} ${{RESOURCE_GROUP_SYSTEM}} ${{CLUSTER_NAME_SYSTEM}} ${{NAMESPACE_SYSTEM}}\
${{SUBSCRIPTION_ID_USER}} ${{RESOURCE_GROUP_USER}} ${{CLUSTER_NAME_USER}} ${{NAMESPACE_USER}}"
```
## Running server-monitor in CLI

### Installation
```
pip3 install -e . 
```
### Command: Generate

#### Sub-command: system-app-graphs

```
server-monitor generate system-app-graphs [OPTIONS] 
                        system-apps-filepath output-dir 
                        tenent-id client-id client-secret workspace-id 
                        subscription-id resource-group cluster-name namespace 
                        start-datetime end-datetime
```
Creates memory and CPU graphs for the system components defined in the text file in the `system-apps-filepath`. The graphs are saved in the `output-dir`.

#### Sub-command: user-app-graphs

```
server-monitor generate user-app-graphs [OPTIONS] 
                        user-apps-filepath output-dir 
                        tenent-id client-id client-secret workspace-id organization-name
                        subscription-id resource-group cluster-name namespace 
                        start-datetime end-datetime
```
Creates memory and CPU graphs for the user apps defined in the text file in the `user-apps-filepath`. it also creates graphs for `average cpu usage per user app` and `average memory usage per user app`, containing averages usages for all apps. The graphs are saved in the `output-dir`.

#### Sub-command: summary-report
```
server-monitor generate summary-report [OPTIONS] graphs-dir 
```
Traverse the `graph-dir` and its sub-directories to create a PDF containing all graphs for system and user apps.
