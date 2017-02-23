#!/bin/bash
i=0
nmcli -m multiline connection | grep UUID >nmcli_out
cat nmcli_out

while read  n u  ; do
	name[$i]=$n
	uuid[$i]=$u
	i=`expr $i + 1`
done < nmcli_out

lenuuid=${#uuid[@]}
count=0
while [ $count -lt $lenuuid ]; do
	echo ${uuid[$count]}
	echo nmcli connection delete uuid ${uuid[$count]}
	let count=count+1
done
