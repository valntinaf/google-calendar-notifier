#!/bin/bash

mv ./* /opt/google-calendar-notifier
echo "* * * * * /bin/python3.8 /opt/google-calendar-notifier" >> crontab -e  
