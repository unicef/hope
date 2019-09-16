#!/usr/bin/env bash
pip install python-crontab==2.3.5
python setup_crons.py && python manage.py process_tasks
