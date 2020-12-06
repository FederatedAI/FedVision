#!/usr/bin/env bash

function download {
  if [ "$(uname)" == "Darwin" ];then
    wget "https://github.com/pseudomuto/protoc-gen-doc/releases/download/v1.3.2/protoc-gen-doc-1.3.2.darwin-amd64.go1.12.6.tar.gz" -O protoc-gen-doc.tar.gz
    tar -xvf protoc-gen-doc.tar.gz
    mv protoc-gen-doc-1.3.2.darwin-amd64.go1.12.6 protoc-gen-doc
  elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    wget "https://github.com/pseudomuto/protoc-gen-doc/releases/download/v1.3.2/protoc-gen-doc-1.3.2.linux-amd64.go1.12.6.tar.gz" -O protoc-gen-doc.tar.gz
    tar -xvf protoc-gen-doc.tar.gz
    mv protoc-gen-doc-1.3.2.linux-amd64.go1.12.6 protoc-gen-doc
  fi
}

mkdir -p _build
cd _build || exit
download
cd ..
protoc \
  --plugin=protoc-gen-doc=./_build/protoc-gen-doc/protoc-gen-doc \
  --doc_out=./_build \
  --doc_opt=markdown,proto.md \
  fedvision/framework/protobuf/*.proto

cp _build/proto.md ../docs/apis/proto.md
rm -rf _build
