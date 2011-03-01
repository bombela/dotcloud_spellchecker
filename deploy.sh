#!/bin/bash
# François-Xavier Bourlet <bombela@gmail.com>

SERVICES=${@:-"worker train"}

for service in $SERVICES
do
	case $service in
		worker)
			for i in $(seq 3)
			do
				dotcloud push spell.worker$i worker
			done
			;;
		*)
			echo "unknown service $service"
			;;
	esac
done
