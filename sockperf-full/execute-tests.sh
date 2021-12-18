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

cluster_ip=""
scenario_name=""
github_token=""
payload_size="0"
concurrent_users=""
github_hook=""
pat_token=""

function usage() {
    echo ""
    echo "Usage: "
    echo "$0 [-c <cluster_ip>] [-s scenario_name] [-t github_token] [-p payload_size] [-u concurrent_users] [-h]"
    echo ""
    echo "-c: Kubernetes cluster IP"
    echo "-s: Test scenario name"
    echo "-t: Github token for the repository"
    echo "-p: Payload size"
    echo "-u: Concurrent users for the test"
    echo ""
}

while getopts "c:s:t:p:u:d:h" opts; do
    case $opts in
    c)
        cluster_ip=${OPTARG}
        ;;
    s)
        scenario_name=${OPTARG}
        ;;
    t)
        github_token=${OPTARG}
        ;;
    w)
        pat_token=${OPTARG}
        ;;
    p)
        payload_size=${OPTARG}
        ;;
    u)
        concurrent_users=${OPTARG}
        ;;
    d)
        github_hook=${OPTARG}
        ;;
    h)
        usage
        exit 0
        ;;
    \?)
        usage
        exit 1
        ;;
    esac
done

if [[ -z $cluster_ip ]]; then
    echo "Please provide the cluster ip."
    exit 1
fi

if [[ -z $scenario_name ]]; then
    echo "Please provide the scenario name."
    exit 1
fi

if [[ -z $concurrent_users ]]; then
    echo "Please provide the number of concurrent users."
    exit 1
fi

rm -rf ~/uploads
REPO_NAME="ballerina-performance-cloud"
rm -rf ~/"${REPO_NAME}"/tests/"$scenario_name"/results

timestamp=$(date +%s)
branch_name="nightly-$scenario_name-${timestamp}"

sockperf ping-pong -i "$cluster_ip" -t 600 --msg-size 1400 --tcp
echo ""
sockperf tp -i "$cluster_ip" -t 600 --msg-size 1400 --tcp

pushd "${REPO_NAME}"
git checkout -b "${branch_name}"
git config --global user.email "ballerina-bot@ballerina.org"
git config --global user.name "ballerina-bot"
git status
git remote -v

popd

payload_flags=""
if [[ $payload_size != "0" ]]; then
    echo "--------Generating $payload_size Payload--------"
    rm -rf "$payload_size""B.json"
    generate-payloads.sh -p array -s "$payload_size"
    payload_flags+=" -Jresponse_size=$payload_size -Jpayload=$(pwd)/$payload_size""B.json"
    echo payload_flags
    echo "--------End of generating payload--------"
fi

echo "--------Running test $scenario_name--------"
pushd "${REPO_NAME}"/tests/"$scenario_name"/scripts/
dstat --noheaders --nocolor --output dstat-client.csv 5 > /dev/null &
start_time=$(date +%Y-%m-%dT%H:%M -u)
sed -i "s/bal.perf.test/${cluster_ip}/g" run.sh
chmod +x run.sh
./run.sh -s "$scenario_name" -u "$concurrent_users" -f "$payload_flags"
end_time=$(date +%Y-%m-%dT%H:%M -u)
kill %1
popd
echo "--------End test--------"

echo "--------Processing Results--------"
pushd "${REPO_NAME}"/tests/"$scenario_name"/results/
cp ../scripts/dstat-client.csv .
echo "$start_time" > test_start_time_utc
echo "$end_time" > test_end_time_utc
echo "--------Splitting Results--------"
jtl-splitter.sh -- -f original.jtl -t 120 -u SECONDS -s
ls -ltr
echo "--------Splitting Completed--------"

echo "--------Generating CSV--------"
sudo bash /base-image/apache-jmeter-5.4/bin/JMeterPluginsCMD.sh --generate-csv summary.csv --input-jtl original-measurement.jtl --plugin-type AggregateReport
echo "--------CSV generated--------"

mkdir ~/uploads
cp -r ~/"${REPO_NAME}"/tests/"$scenario_name"/results ~/uploads

cat summary.csv

if [[ ! -z $github_hook ]]; then
    buildTime=`date +%s`
    echo "CSV modification started"
    # Append Date header
    sed -i ' 1 s/.*/&,Date/' summary.csv
    # Append Date value
    sed -i " 2 s/.*/&,${buildTime}/" summary.csv
    # Append Payload header
    sed -i ' 1 s/.*/&,Payload/' summary.csv
    # Append Payload value
    sed -i " 2 s/.*/&,${payload_size}/" summary.csv
    # Append Users header
    sed -i ' 1 s/.*/&,Users/' summary.csv
    # Append Users value
    sed -i " 2 s/.*/&,${concurrent_users}/" summary.csv

    STATUS="success"
    SUMMARY_STRING=$(sed '3d' summary.csv)

    DATA_STRING=$( jq -n \
                  --arg status "$STATUS" \
                  --arg summary "$SUMMARY_STRING" \
                  '{"event_type": "build", "client_payload": { "status": $status, "result": $summary}}' )

    curl -X POST \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $pat_token" \
        --data $DATA_STRING \
        https://api.github.com/repos/xlight05/ballerina-performance-cloud/dispatches
fi

if [[ -z $github_token ]]; then
    echo "Git Push Skipped"
    exit 0
fi

echo "--------Merge CSV--------"
create-csv.sh summary.csv ~/"${REPO_NAME}"/summary/"$scenario_name".csv "$payload_size" "$concurrent_users"
echo "--------CSV merged--------"
popd

echo "--------Committing CSV--------"
pushd "${REPO_NAME}"
git clean -xfd
git add summary/
git commit -m "Update $scenario_name test results on $(date)"
git push origin "${branch_name}"
popd
echo "--------CSV committed--------"
echo "--------Results processed--------"
