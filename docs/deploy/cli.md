# CLI

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `deploy`: deploy tools
* `services`: services [start|stop] tools
* `template`: template tools

## `deploy`

deploy tools

**Usage**:

```console
$ deploy [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `deploy`

### `deploy deploy`

**Usage**:

```console
$ deploy deploy [OPTIONS]
```

**Options**:

* `--config FILE`: [required]
* `--help`: Show this message and exit.

## `services`

services [start|stop] tools

**Usage**:

```console
$ services [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `all`: [start|stop] all services
* `cluster-manager`: [start|stop] cluster manager service
* `cluster-worker`: [start|stop] cluster worker service
* `coordinator`: [start|stop] coordinator service
* `master`: [start|stop] master service

### `services all`

[start|stop] all services

**Usage**:

```console
$ services all [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `start`: start all services
* `stop`: stop all services

#### `services all start`

start all services

**Usage**:

```console
$ services all start [OPTIONS] CONFIG
```

**Arguments**:

* `CONFIG`: [required]

**Options**:

* `--help`: Show this message and exit.

#### `services all stop`

stop all services

**Usage**:

```console
$ services all stop [OPTIONS] CONFIG
```

**Arguments**:

* `CONFIG`: [required]

**Options**:

* `--help`: Show this message and exit.

### `services cluster-manager`

[start|stop] cluster manager service

**Usage**:

```console
$ services cluster-manager [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `start`: start cluster manager
* `stop`: stop cluster manager

#### `services cluster-manager start`

start cluster manager

**Usage**:

```console
$ services cluster-manager start [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR MANAGER_PORT
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `MANAGER_PORT`: port number for cluster manager to serve  [required]

**Options**:

* `--help`: Show this message and exit.

#### `services cluster-manager stop`

stop cluster manager

**Usage**:

```console
$ services cluster-manager stop [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR MANAGER_PORT
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `MANAGER_PORT`: port number for cluster manager to serve  [required]

**Options**:

* `--help`: Show this message and exit.

### `services cluster-worker`

[start|stop] cluster worker service

**Usage**:

```console
$ services cluster-worker [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `start`: start cluster worker
* `stop`: stop cluster worker

#### `services cluster-worker start`

start cluster worker

**Usage**:

```console
$ services cluster-worker start [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR NAME LOCAL_IP PORT_START PORT_END MAX_TASKS CLUSTER_MANAGER_ADDRESS
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `NAME`: worker name  [required]
* `LOCAL_IP`: local ip  [required]
* `PORT_START`: port start  [required]
* `PORT_END`: port start  [required]
* `MAX_TASKS`: num of maximum parallel tasks  [required]
* `CLUSTER_MANAGER_ADDRESS`: cluster manager address  [required]

**Options**:

* `--data-dir TEXT`: data dir
* `--help`: Show this message and exit.

#### `services cluster-worker stop`

stop cluster worker

**Usage**:

```console
$ services cluster-worker stop [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR NAME
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `NAME`: worker name  [required]

**Options**:

* `--help`: Show this message and exit.

### `services coordinator`

[start|stop] coordinator service

**Usage**:

```console
$ services coordinator [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `start`: start coordinator
* `stop`: stop coordinator

#### `services coordinator start`

start coordinator

**Usage**:

```console
$ services coordinator start [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR COORDINATOR_PORT
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `COORDINATOR_PORT`: port number for coordinator to serve  [required]

**Options**:

* `--help`: Show this message and exit.

#### `services coordinator stop`

stop coordinator

**Usage**:

```console
$ services coordinator stop [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR COORDINATOR_PORT
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `COORDINATOR_PORT`: port number for coordinator to serve  [required]

**Options**:

* `--help`: Show this message and exit.

### `services master`

[start|stop] master service

**Usage**:

```console
$ services master [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `start`: start master
* `stop`: stop master

#### `services master start`

start master

**Usage**:

```console
$ services master start [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR SUBMIT_PORT PARTY_ID CLUSTER_MANAGER_ADDRESS COORDINATOR_ADDRESS
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `SUBMIT_PORT`: submit port  [required]
* `PARTY_ID`: party id  [required]
* `CLUSTER_MANAGER_ADDRESS`: cluster manager address  [required]
* `COORDINATOR_ADDRESS`: coordinator address  [required]

**Options**:

* `--help`: Show this message and exit.

#### `services master stop`

stop master

**Usage**:

```console
$ services master stop [OPTIONS] MACHINE_SSH MACHINE_BASE_DIR SUBMIT_PORT
```

**Arguments**:

* `MACHINE_SSH`: machine ssh string: user@host:port  [required]
* `MACHINE_BASE_DIR`: deployed base name  [required]
* `SUBMIT_PORT`: submit port  [required]

**Options**:

* `--help`: Show this message and exit.

## `template`

template tools

**Usage**:

```console
$ template [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `generate`: generate template
* `standalone`: generate template for standalone deploy

### `template generate`

generate template

**Usage**:

```console
$ template generate [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `template standalone`

generate template for standalone deploy

**Usage**:

```console
$ template standalone [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
