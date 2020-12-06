protobuf:
	sh proto/build.sh

.PHONY: clean
clean:
	rm -rf fedvision/framework/protobuf
	rm -rf logs
