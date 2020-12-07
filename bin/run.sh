DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PaddleDetection="$(dirname $DIR)/deps/PaddleDetection"
Fedvision="$(dirname $DIR)/fedvision"
export PYTHONPATH="$PYTHONPATH:$PaddleDetection:$Fedvision"

# todo: use yaml or json

export num_party=5

python -m fedvision.framework.cli.coordinator --port 10001 > /dev/null 2>&1 &
python -m fedvision.framework.cli.cluster_manager --port 10000 > /dev/null 2>&1 &
python -m fedvision.framework.cli.cluster_worker --name worker --worker-ip 127.0.0.1 --port-start 11000 --port-end 12000 --max-tasks 10 --manager-address 127.0.0.1:10000 > /dev/null 2>&1 &

for ((i=0;i<$((num_party + 0));i++))
do
  python -m fedvision.framework.cli.master --party-id party$i --submitter-port $((10002 + i)) --cluster-address 127.0.0.1:10000 --coordinator-address 127.0.0.1:10001 > /dev/null 2>&1 &
  sleep 0.1
done

