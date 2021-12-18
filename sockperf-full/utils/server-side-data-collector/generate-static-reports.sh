#!/bin/bash

#APPLICATION_LIST_FILE=$1
CLIENT_ID=${1}
CLIENT_SECRET=${2}
CLUSTER_NAME_SYSTEM=${3}
NAMESPACE_SYSTEM="default"
ORG_NAME="not"
RESOURCE_GROUP_SYSTEM=${4}
SUBSCRIPTION_ID_SYSTEM=${5}
SYSTEM_DIRECTORY=${6}
TENANT_ID=${7}
RESULTS_DIR=${8}
TEST_NAME="test_app"
WORKSPACE_ID=${9}
START_TIME=${10}
END_TIME=${11}


docker container run \
  --workdir /perf-test \
  --mount type=bind,source=$SYSTEM_DIRECTORY,target=/perf-test \
  --mount type=bind,source=$RESULTS_DIR,target=/output \
  --rm \
  python:3.9.4 \
  bash -c "pip install -e . \
  && bash /perf-test/runServerMonitor.sh \
       /output \
       $TEST_NAME \
       $TENANT_ID \
       $CLIENT_ID \
       $CLIENT_SECRET \
       $WORKSPACE_ID \
       $ORG_NAME \
       /perf-test/system.txt \
       /conf/user.txt \
       $START_TIME \
       $END_TIME \
       $SUBSCRIPTION_ID_SYSTEM \
       $RESOURCE_GROUP_SYSTEM \
       $CLUSTER_NAME_SYSTEM \
       $NAMESPACE_SYSTEM"
