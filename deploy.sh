#!/bin/bash
# François-Xavier Bourlet <bombela@gmail.com>

SERVICES=${@:-"worker train"}

for service in $SERVICES
do
	case $service in
		worker)
			for i in $(seq 3)
			do
				dotcloud push spell.worker$i worker &
			done
			;;
		train)
			dotcloud push spell.train train &
			;;
		*)
			echo "unknown service to deploy: $service"
			;;
	esac
done

wait
