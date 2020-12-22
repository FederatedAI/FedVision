#!/bin/bash

# Copyright (c) 2020 The FedVision Authors. All Rights Reserved.
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

DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
PROJECT_BASE=$(dirname "${DIR}")

# shellcheck source=env.sh
. "${PROJECT_BASE}/sbin/env.sh"
# shellcheck source=service.sh
. "${PROJECT_BASE}/sbin/service.sh"

usage="Usage: cluster_worker.sh (start|stop) <unique worker name> [<local ip> <port for serve start> <port for serve end> <max tasks> <cluster manager address> <data base dir>]"
if [ $# -le 1 ]; then
  echo "$usage"
  exit 1
fi

if [ -z "${FEDVISION_PYTHON_EXECUTABLE}" ]; then
  echo "fedvision python executable not set"
  exit 1
fi

start_cluster_worker() {
  local pid
  pid=$(
    ps aux | grep "fedvision.framework.cli.cluster_worker" | grep "name ${1}" | grep -v grep | awk '{print $2}'
  )
  if [[ -z ${pid} ]]; then
    mkdir -p "$PROJECT_BASE/logs/nohup"
    nohup "${FEDVISION_PYTHON_EXECUTABLE}" -m fedvision.framework.cli.cluster_worker --name "$1" --worker-ip "$2" --port-start "$3" --port-end "$4" --max-tasks "$5" --manager-address "$6" --data-base-dir "$7" >>"${PROJECT_BASE}/logs/nohup/worker" 2>&1 &
    for ((i = 1; i <= 20; i++)); do
      sleep 0.1
      pid=$(
        ps aux | grep "fedvision.framework.cli.cluster_worker" | grep "name ${1}" | grep -v grep | awk '{print $2}'
      )
      if [[ -n ${pid} ]]; then
        echo "cluster worker service start successfully. pid: ${pid}"
        exit 0
      fi
    done
    echo "cluster worker service start failed"
    exit 1
  else
    echo "cluster worker service named <$1> already started. pid: $pid"
    exit 1
  fi
}

stop_cluster_worker() {
  local pid
  pid=$(
    ps aux | grep "fedvision.framework.cli.cluster_worker" | grep "name ${1}" | grep -v grep | awk '{print $2}'
  )
  if [[ -n ${pid} ]]; then
    echo "killing: $(ps aux | grep "${pid}" | grep -v grep)"
    for ((i = 1; i <= 20; i++)); do
      sleep 0.1
      kill "${pid}"
      pid=$(
        ps aux | grep "fedvision.framework.cli.cluster_worker" | grep "name ${1}" | grep -v grep | awk '{print $2}'
      )
      if [[ -z ${pid} ]]; then
        echo "killed by SIGTERM"
        exit 0
      fi
    done
    if [[ $(kill -9 "${pid}") -eq 0 ]]; then
      echo "killed by SIGKILL"
      exit 0
    else
      echo "Kill error"
      exit 1
    fi
  else
    echo "cluster worker named <${1}> service not running"
    exit 1
  fi
}

case "$1" in
start)
  start_cluster_worker "$2" "$3" "$4" "$5" "$6" "$7" "$8"
  exit 0
  ;;
stop)
  stop_cluster_worker "$2"
  exit 0
  ;;
*)
  echo bad command
  echo "$usage"
  exit 1
  ;;
esac
