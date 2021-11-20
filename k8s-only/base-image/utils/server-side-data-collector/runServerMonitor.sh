#!/bin/bash

# Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
# This software is the property of WSO2 Inc. and its suppliers, if any.
# Dissemination of any information or reproduction of any material contained
# herein is strictly forbidden, unless permitted by WSO2 in accordance with
# the WSO2 Commercial License available at http://wso2.com/licenses.
# For specific language governing the permissions and limitations under
# this license, please see the license as well as any agreement you’ve
# entered into with WSO2 governing the purchase of this software and any

set -e

RESULTS_ROOT_DIR=${1}
# echo "Test Root Dir :" ${RESULTS_ROOT_DIR}
TEST_NAME=${2}
# echo "Test Name :" ${TEST_NAME}
# Auth related parameters
TENENT_ID=${3}
# echo "Tenet ID :" ${TENENT_ID}
CLIENT_ID=${4}
# echo "Client ID :" ${CLIENT_ID}
CLIENT_SECRET=${5}
# echo "Client Secret :" ${CLIENT_SECRET}
WORKSPACE_ID=${6}
# echo "Workspace ID :" ${WORKSPACE_ID}

ORGANIZATION_NAME=${7}
# echo "Org  :" ${ORGANIZATION_NAME}
SYSTEM_FILE=${8}
# echo "System File  :" ${SYSTEM_FILE}
USER_FILE=${9}
# echo "User File  :" ${USER_FILE}
START_DATETIME=${10}
# echo "Start time  :" ${START_DATETIME}
END_DATETIME=${11}
# echo "End time  :" ${END_DATETIME}

# System components' K8s cluster related parameters
SUBSCRIPTION_ID_SYSTEM=${12}
# echo "Subs Id  :" ${SUBSCRIPTION_ID_SYSTEM}
RESOURCE_GROUP_SYSTEM=${13}
# echo "Res group  :" ${RESOURCE_GROUP_SYSTEM}
CLUSTER_NAME_SYSTEM=${14}
# echo "Cluster name  :" ${CLUSTER_NAME_SYSTEM}
NAMESPACE_SYSTEM=${15}
# echo "name space  :" ${NAMESPACE_SYSTEM}

## User apps' K8s cluster related parameters
#SUBSCRIPTION_ID_USER=${16}
#RESOURCE_GROUP_USER=${17}
#CLUSTER_NAME_USER=${18}
#NAMESPACE_USER=${19}

# Optional argument
REQUIRE_USER_APP_DATA=${20:-false}

echo -e "Collecting information for Test ${TEST_NAME} from [${START_DATETIME}] to [${END_DATETIME}] ..."

SERVER_DATA_DIR=${RESULTS_ROOT_DIR}
SYSTEM_DATA_DIR=${RESULTS_ROOT_DIR}/system-app-data
#USER_DATA_DIR=${RESULTS_ROOT_DIR}/server-side-data/user-app-data

mkdir -p ${SERVER_DATA_DIR}
mkdir -p ${SYSTEM_DATA_DIR}

echo "Creating graphs for system apps"
echo ${SYSTEM_FILE}
server-monitor generate system-app-graphs ${SYSTEM_FILE} ${SYSTEM_DATA_DIR} ${TENENT_ID} ${CLIENT_ID} ${CLIENT_SECRET} ${WORKSPACE_ID} \
${SUBSCRIPTION_ID_SYSTEM} ${RESOURCE_GROUP_SYSTEM} ${CLUSTER_NAME_SYSTEM} ${NAMESPACE_SYSTEM} ${START_DATETIME} ${END_DATETIME}

#if [ "$REQUIRE_USER_APP_DATA" = true ] ; then
#    echo "Creating graphs for user apps"
#    mkdir -p ${USER_DATA_DIR}
#    server-monitor generate user-app-graphs ${USER_FILE} ${USER_DATA_DIR} ${TENENT_ID} ${CLIENT_ID} ${CLIENT_SECRET} ${WORKSPACE_ID} ${ORGANIZATION_NAME} \
#    ${SUBSCRIPTION_ID_USER} ${RESOURCE_GROUP_USER} ${CLUSTER_NAME_USER} ${NAMESPACE_USER} ${START_DATETIME} ${END_DATETIME}
#fi

echo "Creating final report"
server-monitor generate summary-report ${SERVER_DATA_DIR}

echo "Completed processing server-side data"
