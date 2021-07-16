# HealthPi

This repository hosts my implementation of monitoring the health values of my Raspberry Pi. 
Each node in my network has an evaluation tool called temperature.py that cronically sends CPU load, 
temperature and other metrics to a central logging instance. The central logging instance evaluates the 
incoming data in a dashboard and displays it via plotly/dash. 

![HealthPi_Dash](/images/dashboard.png)
<br/><br/>

## Node Configuration

Each node in the monitored cluster has a cronjob that calls the evaluation script every 10 seconds and sends the data to a central server via syslog.
