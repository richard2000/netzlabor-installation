#!/bin/bash
i=0
grep -i keinpasswort * -H | xargs -n 1 > nm_ids
cat nm_ids
nmcli -f uuid connection > nmcli_out
#cat nmcli_out
static_connection="ff1d4bde-051c-408b-82dd-664190747d04"
while read  n   ; do
	name[$i]=$n
	i=`expr $i + 1`
done < nm_ids

lenname=${#name[@]}
count=1
while [ $count -lt $lenname ]; do
	echo ${name[$count]}
	if [ "${name[$count],,}" != "${static_connection}" ] 
	then
		echo nmcli connection delete  ${name[$count]}
	else 
		echo "static-Connection found. Nothing to delete" ${name[$count]}
	fi
	let count=count+1
done
