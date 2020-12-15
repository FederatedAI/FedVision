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


import os.path
import shutil
import tarfile
import tempfile

import grpc_tools.protoc
import pkg_resources
import requests
import typer
import yaml

app = typer.Typer()


_base_path = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir))
_proto_path = os.path.abspath(os.path.join(_base_path, "proto"))
_config_path = os.path.abspath(os.path.join(_proto_path, "build_config.yaml"))


@app.command()
def build():
    """
    generate proto buffer files
    """
    proto_include = pkg_resources.resource_filename("grpc_tools", "_proto")
    with open(_config_path) as f:
        config = yaml.safe_load(f)
    proto = set(config.get("proto", []))
    grpc = set(config.get("grpc", []))

    for filename in proto:
        args = [
            "",
            f"-I{proto_include}",
            f"-I{_proto_path}",
            f"--python_out={_base_path}",
        ]
        if filename in grpc:
            args.append(f"--grpc_python_out={_base_path}")
        file_path = os.path.join(_proto_path, filename)
        args.append(file_path)
        if grpc_tools.protoc.main(args) != 0:
            raise Exception(f"build {file_path} failed")

    typer.echo(f"build success")


@app.command()
def clean(dry: bool = typer.Option(False, help="dry run")):
    """
    clean generated files
    """
    with open(_config_path) as f:
        config = yaml.safe_load(f)
    proto = set(config.get("proto", []))
    grpc = set(config.get("grpc", []))

    for filename in proto:
        path = os.path.join(_base_path, filename.replace(".proto", "_pb2.py"))
        if os.path.exists(path):
            if dry:
                typer.echo(f"remove {path}")
            else:
                os.remove(path)
    for filename in grpc:
        path = os.path.join(_base_path, filename.replace(".proto", "_pb2_grpc.py"))
        if os.path.exists(path):
            if dry:
                typer.echo(f"remove {path}")
            else:
                os.remove(path)
    typer.echo(f"clean success")


@app.command()
def doc():
    """
    build proto buffer docs
    """

    url_base = "https://github.com/pseudomuto/protoc-gen-doc/releases/download/v1.3.2/"
    if os.uname().sysname == "Darwin":
        download_url = f"{url_base}/protoc-gen-doc-1.3.2.darwin-amd64.go1.12.6.tar.gz"
    elif os.uname().sysname == "Linux":
        download_url = f"{url_base}/protoc-gen-doc-1.3.2.linux-amd64.go1.12.6.tar.gz"
    else:
        raise Exception(f"{os.uname().sysname} not supported")

    # process in temp dir
    with tempfile.TemporaryDirectory() as d:
        # download
        req = requests.get(download_url, stream=True)
        if req.status_code != 200:
            raise RuntimeError(
                f"Downloading from {download_url} failed with code {req.status_code}!"
            )
        target_name = os.path.join(d, "protoc-gen-doc.tar.gz")
        total_size = req.headers.get("content-length")
        with open(target_name, "wb") as f:
            if total_size:
                with typer.progressbar(
                    req.iter_content(chunk_size=1024),
                    length=(int(total_size) + 1023) // 1024,
                ) as bar:
                    for chunk in bar:
                        f.write(chunk)
            else:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        # extract
        with tarfile.open(os.path.join(d, target_name), "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("protoc-gen-doc"):
                    tar.extract(member, path=d)
                    shutil.move(
                        os.path.join(d, member.name), os.path.join(d, "protoc-gen-doc")
                    )

        # generate doc
        proto_include = pkg_resources.resource_filename("grpc_tools", "_proto")
        with open(_config_path) as f:
            config = yaml.safe_load(f)
        proto = set(config.get("proto", []))

        cmd = [
            "",
            f"--plugin=protoc-gen-doc={os.path.join(d, 'protoc-gen-doc')}",
            f"--doc_out={os.path.join(_base_path, 'docs', 'apis')}",
            "--doc_opt=markdown,proto.md",
            f"-I{proto_include}",
            f"-I{_proto_path}",
        ]
        for filename in proto:
            cmd.append(os.path.join(_proto_path, filename))
        if not grpc_tools.protoc.main(cmd) == 0:
            raise RuntimeError("generate proto doc failed")

        typer.echo("generate proto doc success")


if __name__ == "__main__":
    app()
