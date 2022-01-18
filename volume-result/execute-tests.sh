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
echo "Executing script"
sudo mkdir /results/hello
sudo mkdir /results/foo
sudo mkdir /results/bar

echo "HTTP Request,3377166,63,13,283,326,349,0,1025,0.00%,3127.3,3731.8,101.75,1642319492,1024,50" > summary1.csv
cat summary1.csv | sudo tee /results/hello/summary.csv

echo "HTTP Request,3377166,63,13,283,326,349,0,1025,0.00%,3127.3,3731.8,101.75,1642319492,1024,100" > summary2.csv
cat summary2.csv | sudo tee /results/foo/summary.csv

echo "HTTP Request,3377166,63,13,283,326,349,0,1025,0.00%,3127.3,3731.8,101.75,1642319492,1024,200" > summary3.csv
cat summary3.csv | sudo tee /results/bar/summary.csv
sleep 60s
echo "After sleep"