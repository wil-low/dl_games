#/bin/bash

start_seed=$1
workers=10

for i in `seq $workers`
do
	let "worker_seed = $start_seed + $i"
	python aucteraden.py -s $worker_seed -n 1000 -1 &
done
