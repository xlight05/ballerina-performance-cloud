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

from setuptools import setup, find_packages

setup(
    name="server-monitor",
    version="0.0.2",
    description="Collect Memory and CPU data from Azure log analytics workspace and create reports",
    packages=find_packages(),
    py_modules=["application"],
    install_requires=[
        "click==7.1.2",
        "azure-loganalytics==0.1.0",
        "matplotlib==3.4.1",
        "numpy==1.20.2",
        "pandas==1.2.3",
        "Pillow==8.1.2",
        "seaborn==0.11.1",
    ],
    entry_points="""
            [console_scripts]
            server-monitor=application.cli_interface:main
    """,
)
