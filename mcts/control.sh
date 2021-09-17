#!/bin/sh

function startOne(){
	/usr/bin/python practice.py $1 >/dev/null 2>&1 &
	#sleep $1 &
	pid=$!
	echo $pid >> ./practice.pid
}

function start(){
    >./practice.pid
    nodeIds=$(cat ./practice_node_ids)
    for nodeid in $nodeIds
    do  
        startOne $nodeid
    done        
}

function stop(){
	pids=$(cat ./practice.pid)
    for pid in $pids
    do
        kill -15 $pid
    done
}

function usage() {
    echo "Usage: $0 {start|stop}"
    exit 1
}

if [ $# != 1 ]; then
    usage
fi

case "$1" in
    start|stop)
        $1
        ;;
    *)
        usage
esac
