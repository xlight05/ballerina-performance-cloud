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

dispatch_type=""
function usage() {
    echo ""
    echo "Usage: "
    echo "$0 [-c <cluster_ip>] [-s scenario_name] [-t github_token] [-p payload_size] [-u concurrent_users] [-h]"
    echo ""
    echo "-r: Name of the repo containing tests"
    echo "-c: Kubernetes cluster IP"
    echo "-s: Test scenario name"
    echo "-t: Github token for the repository"
    echo "-p: Payload size"
    echo "-u: Concurrent users for the test"
    echo "-i: Space ID of the chat room"
    echo "-m: Message Key of the chat"
    echo "-a: Chat token"
    echo "-b: branch name"
    echo "-d: Repository dispatch type"
    echo ""
}

while getopts "d:h" opts; do
    case $opts in
    d)
        dispatch_type=${OPTARG}
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

echo $dispatch_type

if [[ ! -z $dispatch_type ]]; then
    echo "dispatch type entered "
else
    echo "dispatch type not entered"
fi
