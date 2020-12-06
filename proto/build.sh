#!/usr/bin/env bash


function build_framework() {
  mkdir -p ../fedvision/framework/protobuf
  touch ../fedvision/framework/protobuf/__init__.py
  python3 -m grpc_tools.protoc -I. --python_out=.. fedvision/framework/protobuf/file.proto
  python3 -m grpc_tools.protoc -I. --python_out=.. fedvision/framework/protobuf/job.proto
  python3 -m grpc_tools.protoc -I. --python_out=.. --grpc_python_out=.. fedvision/framework/protobuf/cluster.proto
  python3 -m grpc_tools.protoc -I. --python_out=.. --grpc_python_out=.. fedvision/framework/protobuf/coordinator.proto
}

function build_paddle_fl() {
  mkdir -p ../fedvision/paddle_fl/protobuf
  touch ../fedvision/paddle_fl/protobuf/__init__.py
  python3 -m grpc_tools.protoc -I. --python_out=.. fedvision/paddle_fl/protobuf/fl_job.proto
  python3 -m grpc_tools.protoc -I. --python_out=.. --grpc_python_out=.. fedvision/paddle_fl/protobuf/scheduler.proto
}

function build() {
    cd "$(dirname $0)" || exit
    pwd
    build_framework
    build_paddle_fl
}

build
