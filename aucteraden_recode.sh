#/bin/bash

start_seed=$1
end_seed=$2

for i in `seq $start_seed $end_seed`
do
	python aucteraden_recode.py -s $i -n 1000
done
