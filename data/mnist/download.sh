DIR="$(
  cd "$(dirname "$0")"
  pwd -P
)"
cd "$DIR"

URL_PREFIX="https://dataset.bj.bcebos.com/mnist/"
TEST_IMAGE="t10k-images-idx3-ubyte.gz"
TEST_LABEL="t10k-labels-idx1-ubyte.gz"
TRAIN_IMAGE="train-images-idx3-ubyte.gz"
TRAIN_LABEL="train-labels-idx1-ubyte.gz"

echo "Downloading..."
wget "${URL_PREFIX}${TEST_IMAGE}"
wget "${URL_PREFIX}${TEST_LABEL}"
wget "${URL_PREFIX}${TRAIN_IMAGE}"
wget "${URL_PREFIX}${TRAIN_LABEL}"

echo "checking"
md5sum --check checksum
