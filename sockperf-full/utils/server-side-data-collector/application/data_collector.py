import errno
import json
import math
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
from application import constants as const
from application.logger_setup import logger
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from PIL import Image

# Image parameter setup
sns.set(font_scale=const.FONT_SCALE)
sns.set_style(
    "ticks",
    {
        "xtick.major.color": "black",
        "axes.facecolor": ".9",
        "figure.facecolor": ".9",
    },
)


def get_app_list(filepath, organization_name=None):
    try:
        with open(filepath, "r") as reader:
            app_list = reader.read().splitlines()
            if organization_name is not None:
                app_list = [organization_name + "-" + app_name for app_name in app_list]
            logger.info(
                "Retrieving usage data for following Choreo components: %s",
                app_list,
            )
    except IOError:
        logger.exception("Error due to unprocessable input:")
        sys.exit(errno.EINTR)
    return app_list


def get_token(tenant_id, client_id, client_secret):
    token_endpoint_url = const.LOGIN_BASE_URL + "/" + tenant_id + const.TOKEN_ENDPOINT

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "Content-Type": "x-www-form-urlencoded",
        "resource": const.LOG_ANALYTICS_API_URL,
    }

    try:
        response = requests.post(token_endpoint_url, data=payload, verify=True)
    except Exception as exception:
        raise Exception("Access token retrieval failed: ") from exception

    if response.status_code == 200:
        logger.info("Access token obtained")
        return json.loads(response.content)["access_token"]
    else:
        logger.info("Message", response.content)
        raise Exception(
            f"Access token retrieval failed with status code: {response.status_code}"
        )


def get_data(query, token, workspace_id):
    log_analytics_query_endpoint = (
        const.LOG_ANALYTICS_API_URL
        + const.WORKSPACES_ENDPOINT
        + "/"
        + workspace_id
        + const.QUERY_ENDPOINT
    )
    query_endpoint_params = {"query": query}
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(
            log_analytics_query_endpoint, params=query_endpoint_params, headers=headers
        )
    except Exception as exception:
        raise Exception("Data retrieval failed: ") from exception

    if response.status_code == 200:
        logger.info("Query ran successfully")
        logger.info(response.content)
        return json.loads(response.content)
    else:
        raise Exception(
            f"Data retrieval failed with status code: {response.status_code}"
        )


def draw_line_plot(data, chart_title, metric_axis_label, output_dir):
    major_locator_distance = math.ceil(len(data["TimeGenerated"]) / 12)
    fig, ax = plt.subplots(figsize=const.FIGURE_DIMENSIONS)
    ax.xaxis.set_major_locator(MultipleLocator(major_locator_distance))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(b=True, which="major", color="w", linewidth=1.3)
    ax.grid(b=True, which="minor", color="w", linewidth=0.5)
    df = data.melt(
        "TimeGenerated", var_name="Measurement", value_name=metric_axis_label
    )
    sns.lineplot(
        x="TimeGenerated", y=metric_axis_label, hue="Measurement", data=df
    ).set_title(chart_title)
    plt.savefig(
        os.path.join(output_dir, chart_title + ".png"),
        orientation="landscape",
        pad_inches=0.5,
    )
    logger.info("Created graph")


def create_graphs(data, output_dir):
    memory_data = None
    cpu_data = None
    logger.info("Processing Memory Usage Data")
    table = pd.DataFrame(
        data=data["tables"][const.MEMORY_TABLE_INDEX]["rows"],
        columns=[
            column["name"]
            for column in data["tables"][const.MEMORY_TABLE_INDEX]["columns"]
        ],
    )
    if not table.empty:
        memory_data, chart_title, metric_units = _process_usage_data(
            table, const.MEMORY_TABLE_INDEX
        )
        draw_line_plot(memory_data, chart_title, metric_units, output_dir)

    logger.info("Processing CPU Usage Data")
    table = pd.DataFrame(
        data=data["tables"][const.CPU_TABLE_INDEX]["rows"],
        columns=[
            column["name"]
            for column in data["tables"][const.CPU_TABLE_INDEX]["columns"]
        ],
    )
    if not table.empty:
        cpu_data, chart_title, metric_units = _process_usage_data(
            table, const.CPU_TABLE_INDEX
        )
        draw_line_plot(cpu_data, chart_title, metric_units, output_dir)

    return memory_data, cpu_data


def _process_usage_data(data, metric):
    chart_title = None
    metric_units = None
    unique_pods = list(data["PodName"].unique())
    time_stamps = json.loads(data["TimeGenerated"][0])
    app_data = pd.DataFrame(time_stamps, columns=["TimeGenerated"])

    for counter_name in ["Request", "Limit"]:
        filter_ = data["CounterName"].str.contains(counter_name)
        filtered_data = data.loc[filter_]

        column_values = json.loads(filtered_data["Measure"].iloc[0])
        column_name = filtered_data["CounterName"].iloc[0]
        column_name = column_name.replace("Bytes", "")
        column_name = column_name.replace("NanoCores", "")
        app_data.insert(len(app_data.columns), column_name, column_values)

    for index, unique_pod in enumerate(unique_pods):
        if metric == const.MEMORY_TABLE_INDEX:
            filter_ = (data["CounterName"].str.contains("memoryWorkingSet")) & (
                data["PodName"] == unique_pod
            )
            if index == 0:
                chart_title = unique_pod.rsplit("-", 2)[0] + " - memory"
                metric_units = "Memory Usage (MiB)"
        elif metric == const.CPU_TABLE_INDEX:
            filter_ = (data["CounterName"].str.contains("cpuUsage")) & (
                data["PodName"] == unique_pod
            )
            if index == 0:
                chart_title = unique_pod.rsplit("-", 2)[0] + " - cpu"
                metric_units = "CPU Usage (millicores)"
        else:
            logger.exception("Unknown Metrics")
            sys.exit(errno.EINTR)
        filtered_data = data.loc[filter_]
        column_values = json.loads(filtered_data["Measure"].iloc[0])
        column_name = unique_pod
        app_data.insert(len(app_data.columns), column_name, column_values)

    app_data["TimeGenerated"] = (
        pd.to_datetime(app_data["TimeGenerated"])
        .dt.tz_localize(None)
        .astype(str)
        .apply(lambda x: x.replace(" ", "\n"))
    )
    return app_data, chart_title, metric_units


def create_pdf(graph_dir):
    image_list = []
    for root, dirs, files in os.walk(graph_dir, topdown=False):
        pdf_name = os.path.split(root)[1]
        for name in files:
            path = os.path.join(root, name)
            if name.endswith(".png"):
                png = Image.open(path).convert("RGB")
                image_list.append(png)

    if len(image_list) >= 2:
        save_path = graph_dir + "/" + pdf_name + "-final-report.pdf"
        image_list[0].save(save_path, save_all=True, append_images=image_list[1:])
    else:
        logger.info("Not enough images to create PDF: Skipping directory: %s", pdf_name)
