#!/bin/bash -e
# Copyright 2021 WSO2 Inc. (http://wso2.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ----------------------------------------------------------------------------
# Running the Load Test
# ----------------------------------------------------------------------------
set -e

DISPATCH_TYPE="perf" #todo fix

pushd /home/anjana/repos/ballerina-performance-cloud/volume-result/results/data
CONTENT=$(for SCENARIO_NAME in *; do 

STATUS="success"
SUMMARY_STRING=$(cat $SCENARIO_NAME/summary.csv)
ERROR_RATE=$(echo $SUMMARY_STRING | cut -d ',' -f10)
ERROR_RATE=$(echo $ERROR_RATE | sed 's/%//')
ERROR_RATE_LIMIT="5.00"
if [ 1 -eq "$(echo "${ERROR_RATE} > ${ERROR_RATE_LIMIT}" | bc)" ]; then
    STATUS="failed"
fi
DATA_STRING=$( jq -n \
                --arg status "$STATUS" \
                --arg summary "$SUMMARY_STRING" \
                --arg errorRate "$ERROR_RATE" \
                --arg scenarioName "${SCENARIO_NAME}" \
                '{ "name": $scenarioName, "status": $status, "result": $summary, "errorRate": $errorRate}' )

echo $DATA_STRING

done | jq -n '.results |= [inputs]')
# echo $CONTENT

FINAL_PAYLOAD=$( jq -n \
                --argjson content "${CONTENT}" \
                --arg eventType "${DISPATCH_TYPE}" \
                '{"event_type": $eventType, "client_payload": $content }' )
echo $FINAL_PAYLOAD

curl -X POST \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    --data "$FINAL_PAYLOAD" \
    "https://api.github.com/repos/ballerina-platform/${REPO_NAME}/dispatches"

popd

# pushd /home/anjana/repos/ballerina-performance-cloud/volume-result/results/data/project-1
# SCENARIO_NAME=${PWD##*/}
# echo "Current scenario" $SCENARIO_NAME
# STATUS="success"
# SUMMARY_STRING=$(cat summary.csv)
# ERROR_RATE=$(echo $SUMMARY_STRING | cut -d ',' -f10)
# ERROR_RATE=$(echo $ERROR_RATE | sed 's/%//')
# ERROR_RATE_LIMIT="5.00"
# if [ 1 -eq "$(echo "${ERROR_RATE} > ${ERROR_RATE_LIMIT}" | bc)" ]; then
#     STATUS="failed"
# fi
# DATA_STRING=$( jq -n \
#                 --arg status "$STATUS" \
#                 --arg summary "$SUMMARY_STRING" \
#                 --arg errorRate "$ERROR_RATE" \
#                 --arg scenarioName "${SCENARIO_NAME}" \
#                 '{ "name": $scenarioName, "status": $status, "result": $summary, "errorRate": $errorRate}' )

# echo $DATA_STRING1


# VAR=($DATA_STRING $DATA_STRING1)

# jq -nc '{var: $ARGS.positional}' --args ${VAR[@]}