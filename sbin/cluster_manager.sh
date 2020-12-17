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

usage="Usage: cluster_manager.sh (start|stop) <port>"
if [ $# -le 1 ]; then
  echo "$usage"
  exit 1
fi

if [ -z "${FEDVISION_PYTHON_EXECUTABLE}" ]; then
  echo "fedvision python executable not set"
  exit 1
fi

start_cluster_manager() {
  local re='^[0-9]+$'
  if ! [[ $1 =~ $re ]]; then
    echo "error: port should be number" >&2
    echo "$usage"
    exit 1
  fi
  mkdir -p "$PROJECT_BASE/logs/nohup"
  nohup "${FEDVISION_PYTHON_EXECUTABLE}" -m fedvision.framework.cli.cluster_manager --port "${1}" >>"${PROJECT_BASE}/logs/nohup/manager" 2>&1 &
}

case "$1" in
start)
  start_service "$2" clustermanager start_cluster_manager "$2"
  exit 0
  ;;
stop)
  stop_service_by_port "$2" clustermanager
  exit 0
  ;;
*)
  echo bad command
  echo "$usage"
  exit 1
  ;;
esac
