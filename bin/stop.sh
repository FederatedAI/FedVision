ps -ef | grep "python -m fedvision" | grep -v grep | awk '{print $2}' | xargs kill -9
