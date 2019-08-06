#!/bin/sh
python test.py &&
	echo "test ok"
python testclick.py -c test1.yaml -c test2.yaml -o logging.level=ERROR &&
	echo "testclick ok"
