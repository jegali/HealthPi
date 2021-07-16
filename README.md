# HealthPi

This repository hosts my implementation of monitoring the health values of my Raspberry Pi. 
Each node in my network has an evaluation tool called temperature.py that cronically sends CPU load, 
temperature and other metrics to a central logging instance. The central logging instance evaluates the 
incoming data in a dahboard and displays it via plotly/dash. 
