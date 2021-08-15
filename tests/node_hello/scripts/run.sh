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
# Execusion script for ballerina performance tests
# ----------------------------------------------------------------------------
set -e
source base-scenario.sh
jmeter -n -t ~/ballerina-performance-cloud/tests/"$scenario_name"/scripts/http-get-request.jmx -l ~/ballerina-performance-cloud/tests/"$scenario_name"/results/original.jtl -Jusers="$concurrent_users" -Jduration=1200 -Jhost=bal.perf.test -Jport=80 -Jprotocol=http -Jpath=hello
