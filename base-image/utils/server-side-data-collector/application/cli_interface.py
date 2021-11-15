"""
 Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
  This software is the property of WSO2 Inc. and its suppliers, if any.
  Dissemination of any information or reproduction of any material contained
  herein is strictly forbidden, unless permitted by WSO2 in accordance with
  the WSO2 Commercial License available at http://wso2.com/licenses.
  For specific language governing the permissions and limitations under
  this license, please see the license as well as any agreement you’ve
  entered into with WSO2 governing the purchase of this software and any
"""

import errno
import os
import sys

import click
import pandas as pd
from application import constants as const
from application.data_collector import (
    create_graphs,
    create_pdf,
    draw_line_plot,
    get_app_list,
    get_data,
    get_token,
)
from application.logger_setup import logger


@click.group()
def main():
    """Create memory and CPU usage graphs and reports"""
    pass


@main.group("generate")
def generate():
    """Generate graphs and reports"""
    pass


@generate.command("user-app-graphs")
@click.argument(
    "user_apps_filepath",
    type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True),
    metavar="user-apps-filepath",
)
@click.argument(
    "output_dir", type=click.Path(exists=True, resolve_path=True), metavar="output-dir"
)
@click.argument("tenent_id", type=click.STRING, metavar="tenent-id")
@click.argument("client_id", type=click.STRING, metavar="client-id")
@click.argument("client_secret", type=click.STRING, metavar="client-secret")
@click.argument("workspace_id", type=click.STRING, metavar="workspace-id")
@click.argument("organization_name", type=click.STRING, metavar="organization-name")
@click.argument("subscription_id", type=click.STRING, metavar="subscription-id")
@click.argument("resource_group", type=click.STRING, metavar="resource-group")
@click.argument("cluster_name", type=click.STRING, metavar="cluster-name")
@click.argument("namespace", type=click.STRING, metavar="namespace")
@click.argument("start_datetime", type=click.STRING, metavar="start-datetime")
@click.argument("end_datetime", type=click.STRING, metavar="end-datetime")
def collect_user_app_data(
    user_apps_filepath,
    output_dir,
    tenent_id,
    client_id,
    client_secret,
    workspace_id,
    organization_name,
    subscription_id,
    resource_group,
    cluster_name,
    namespace,
    start_datetime,
    end_datetime,
):
    """Create memory and CPU usage graphs for user apps"""

    aggregated_memory_data = None
    aggregated_cpu_data = None

    app_list = get_app_list(user_apps_filepath, organization_name)
    token = get_token(tenent_id, client_id, client_secret)

    for app in app_list:
        logger.info("Collecting and processing data for System component: %s", app)
        user_app_query = (
            const.USER_APP_QUERY_TEMPLATE.format(
                subscription_id=subscription_id,
                resource_group=resource_group,
                cluster_name=cluster_name,
                start_date_time=start_datetime,
                end_date_time=end_datetime,
                k8s_namespace=namespace,
                app_name=app,
            )
            + const.CPU_MEMORY_RETRIVAL_QUERY
        )

        try:
            user_app_data = get_data(
                query=user_app_query, token=token, workspace_id=workspace_id
            )

            memory_data, cpu_data = create_graphs(user_app_data, output_dir)

            if memory_data is None or cpu_data is None:
                logger.warn("No data found for the app: %s", app)
                continue

            if aggregated_memory_data is None or aggregated_cpu_data is None:
                aggregated_memory_data = pd.DataFrame(
                    memory_data.iloc[:, const.TIMEGENERATED_COLUMN_INDEX],
                    columns=["TimeGenerated"],
                )
                aggregated_cpu_data = pd.DataFrame(
                    cpu_data.iloc[:, const.TIMEGENERATED_COLUMN_INDEX],
                    columns=["TimeGenerated"],
                )

                # Find request and limit values for CPU and memory
                for df_index, dataframe in enumerate([memory_data, cpu_data]):
                    for column_index in const.COMMON_COLUMNS:
                        column_name = dataframe.columns[column_index]
                        constant_value = 0
                        for row_index, row in dataframe.iterrows():
                            constant_value = dataframe[column_name][row_index]
                            if constant_value != 0:
                                break
                        if df_index == 0:
                            aggregated_memory_data[column_name] = constant_value
                        if df_index == 1:
                            aggregated_cpu_data[column_name] = constant_value

            aggregated_memory_data[app] = memory_data.iloc[
                :, const.POD_DATA_COLUMNS_START_INDEX :
            ].mean(axis=1)
            aggregated_cpu_data[app] = cpu_data.iloc[
                :, const.POD_DATA_COLUMNS_START_INDEX :
            ].mean(axis=1)
        except Exception:
            logger.exception("Graph creation failed for app %s", app)

    if aggregated_memory_data is not None and aggregated_cpu_data is not None:
        draw_line_plot(
            aggregated_memory_data,
            "average memory usage per user app",
            "Memory Usage (MiB)",
            output_dir,
        )
        draw_line_plot(
            aggregated_cpu_data,
            "average cpu usage per user app",
            "CPU Usage (millicores)",
            output_dir,
        )
    else:
        logger.exception("No aggregated data was found")


@generate.command("system-app-graphs")
@click.argument(
    "system_apps_filepath",
    type=click.Path(exists=True, file_okay=True, readable=True),
    metavar="system-apps-filepath",
)
@click.argument(
    "output_dir", type=click.Path(exists=True, resolve_path=True), metavar="output-dir"
)
@click.argument("tenent_id", type=click.STRING, metavar="tenent-id")
@click.argument("client_id", type=click.STRING, metavar="client-id")
@click.argument("client_secret", type=click.STRING, metavar="client-secret")
@click.argument("workspace_id", type=click.STRING, metavar="workspace-id")
@click.argument("subscription_id", type=click.STRING, metavar="subscription-id")
@click.argument("resource_group", type=click.STRING, metavar="resource-group")
@click.argument("cluster_name", type=click.STRING, metavar="cluster-name")
@click.argument("namespace", type=click.STRING, metavar="namespace")
@click.argument("start_datetime", type=click.STRING, metavar="start-datetime")
@click.argument("end_datetime", type=click.STRING, metavar="end-datetime")
def collect_system_app_data(
    system_apps_filepath,
    output_dir,
    tenent_id,
    client_id,
    client_secret,
    workspace_id,
    subscription_id,
    resource_group,
    cluster_name,
    namespace,
    start_datetime,
    end_datetime,
):
    """Create memory and CPU usage graphs for system apps"""
    component_list = get_app_list(system_apps_filepath)
    token = get_token(tenent_id, client_id, client_secret)
    for component in component_list:
        logger.info(
            "Collecting and processing data for System component: %s", component
        )
        system_app_query = (
            const.SYSTEM_APP_QUERY_TEMPLATE.format(
                subscription_id=subscription_id,
                resource_group=resource_group,
                cluster_name=cluster_name,
                start_date_time=start_datetime,
                end_date_time=end_datetime,
                k8s_namespace=namespace,
                choreo_component=component,
            )
            + const.CPU_MEMORY_RETRIVAL_QUERY
        )

        system_app_data = get_data(
            query=system_app_query, token=token, workspace_id=workspace_id
        )
        if system_app_data is not None:
            try:
                create_graphs(system_app_data, output_dir)
            except Exception:
                logger.exception("Graph creation failed for component %s", component)
                sys.exit(errno.EINTR)
        else:
            logger.exception("Data retrieval failed for component %s", component)
            sys.exit(errno.EINTR)


@generate.command("summary-report")
@click.argument(
    "graph_dir", type=click.Path(exists=True, resolve_path=True), metavar="graph-dir"
)
def generate_report(graph_dir):
    """Generate PDF report from all the graphs in a given folder"""
    create_pdf(graph_dir)


if __name__ == "__main__":
    main()
