#!/bin/bash
# François-Xavier Bourlet <bombela@gmail.com>

SERVICES=${@:-"worker monitor train"}

for service in $SERVICES
do
	case $service in
		worker)
			cp -f redisconfig.py celeryconfig.py worker/
			for i in $(seq 3)
			do
				dotcloud push spell.worker$i worker &
			done
			;;
		train)
			cp -f redisconfig.py celeryconfig.py train/
			cp -f worker/{wordcounter.py,spellchecker.py} train/
			dotcloud push spell.train train &
			;;
		monitor)
			cp -f redisconfig.py monitor/
			dotcloud push spell.monitor monitor &
			;;
		*)
			echo "unknown service to deploy: $service"
			;;
	esac
done

wait
