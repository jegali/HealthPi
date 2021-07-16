# HealthPi

This repository hosts my implementation of monitoring the health values of my Raspberry Pi. 
Each node in my network has an evaluation tool called temperature.py that cronically sends CPU load, 
temperature and other metrics to a central logging instance. The central logging instance evaluates the 
incoming data in a dashboard and displays it via plotly/dash. 

![HealthPi_Dash](/images/dashboard.png)
<br/><br/>

## Node Configuration

Each node in the monitored cluster has a cronjob that calls the evaluation script every 10 seconds and sends the data to a central server via syslog.
The table of cronjobs can be accessed via

```bash
crontab -e
```

This command may be called by any user with root privileges. Depending on the operating system, the cronjobs can be set from 
daily recurring to every second. Ubuntu unfortunately only offers a maximum resolution of one second. 
Since I wanted to run the job every 10 seconds, I had to resort to a little trick: 
Using the sleep command, the job is started with a time delay. My crontable looks like this:

```bash
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command

* * * * * /home/jens/health.sh
* * * * * sleep 10; /home/jens/health.sh
* * * * * sleep 20; /home/jens/health.sh
* * * * * sleep 30; /home/jens/health.sh
* * * * * sleep 40; /home/jens/health.sh
* * * * * sleep 50; /home/jens/health.sh
```

being "jens" my user and "/home/jens/health.sh" the path to the script to be executed.
For some more information on how to handle cronjobs, please refer to this web page

https://tecadmin.net/crontab-in-linux-with-20-examples-of-cron-schedule/

If we look at the health.sh script next, we will notice that there is only one Python call that starts the actual script.

```bash
#!/bin/sh

python3 temperature.py
```

So the temperature.py script is where the magic happens. I don't want to post the entire source code here, please have a look at the "node" folder where you can find the script that need to be deployed on the nodes.

## Server Configuration

If the logging server itself is also to be monitored ("quid custodiet custodes?"), two crontables are necessary. On the one hand, the logging server has the cron table that all nodes also have. This table of cronjobs can be accessed via

```bash
crontab -e
```

and looks exactly the same like the one on the nodes:


```bash
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command

* * * * * /home/jens/health.sh
* * * * * sleep 10; /home/jens/health.sh
* * * * * sleep 20; /home/jens/health.sh
* * * * * sleep 30; /home/jens/health.sh
* * * * * sleep 40; /home/jens/health.sh
* * * * * sleep 50; /home/jens/health.sh
```


