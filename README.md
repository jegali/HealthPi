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

Maybe you need to install some python dependencies. Before running the script by cron do a manual run. I had to install psutil by

```bash
sudo apt install python3-pip
pip install psutil
```


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

In addition, I created another crontable for the superuser that takes care of the logrotate. 
Of course Linux can do this on its own, but I wanted a logrotate that happens every hour so that 
the logfiles don't get too big. And who cares about health-data from the day before yesterday.
So I created a new crontable by using

```bash
sudo crontab -e
```

with this content:

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

0 * * * * /usr/sbin/logrotate -f /etc/logrotate.d/raspberryhealth
```

As you may notice, a script called raspberryhealth is used to do the rotating:

```bash
/var/log/raspberry/raspberryhealth
{
        daily
        missingok
        rotate 4
        su syslog adm
        create 664 syslog adm
        size 1M
        postrotate
                /usr/lib/rsyslog/rsyslog-rotate
        endscript
}
```

Please place this script in /etc/logrotate.d/ and name it raspberryhealth, so the cronjob can find it.

Since the logging server has to accept logs from all nodes and has to put them in a dedicated log-file, you have to change the config-file for rsyslog.

```bash
# /etc/rsyslog.conf configuration file for rsyslog
#
# For more information install rsyslog-doc and see
# /usr/share/doc/rsyslog-doc/html/configuration/index.html
#
# Default logging rules can be found in /etc/rsyslog.d/50-default.conf


#################
#### MODULES ####
#################

module(load="imuxsock") # provides support for local system logging
#module(load="immark")  # provides --MARK-- message capability

# provides UDP syslog reception
module(load="imudp")
input(type="imudp" port="514")

# provides TCP syslog reception
module(load="imtcp")
input(type="imtcp" port="514")

# provides kernel logging support and enable non-kernel klog messages
module(load="imklog" permitnonkernelfacility="on")

###########################
#### GLOBAL DIRECTIVES ####
###########################

#
# Use traditional timestamp format.
# To enable high precision timestamps, comment out the following line.
#
#$template FileFormat,"%TIMESTAMP::::date-rfc3339% %HOSTNAME% %syslogtag%%msg::::sp-if-no-1st-sp%%msg::::drop-last-1f%\n
"
#$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat  <-- NEW NEW NEW commented out
$ActionFileDefaultTemplate RSYSLOG_FileFormat              <-- NEW NEW NEW
# Filter duplicated messages
$RepeatedMsgReduction on

#
# Set the default permissions for all log files.
#
$FileOwner syslog
$FileGroup adm
$FileCreateMode 0640
$DirCreateMode 0755
$Umask 0022
$PrivDropToUser syslog
$PrivDropToGroup syslog

#
# Where to place spool and state files
#
$WorkDirectory /var/spool/rsyslog

#
# Include all config files in /etc/rsyslog.d/
#
$IncludeConfig /etc/rsyslog.d/*.conf

:msg, contains, "CPU_" /var/log/raspberry/raspberryhealth     <-- NEW NEW NEW
```

After making the changes to /etc/ryslog.conf, please restart the service by typing 

```bash
sudo service rsyslog restart
```

The main app is a dash app - dash uses flash as webserver.
Dash itself is not so easy to explain, especially the callback functions were tricky to implement. 
I did no further software engineering or cleanup of the code, maybe it can be helpful for you in the future.
You can find the file in the folder logging-server. Start it by typing

```bash
python3 healthapp.py
```

The standard port is 8080, you just have to open up a browser and it should work if you followed all the previous steps.
