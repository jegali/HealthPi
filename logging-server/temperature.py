# -*- coding: utf-8 -*-

import sys
import psutil

import logging
import logging.handlers
import socket

myLog = logging.getLogger('StatsLogger')
myLog.setLevel(logging.DEBUG)

# auf der lokalen maschine address="/dev/log" verwenden
# ansonten die IP der zentralen Logginginstanz eintragen (address=('192.168.178.29',514))
handler = logging.handlers.SysLogHandler(address='/dev/log')
myLog.addHandler(handler)


# get the tenmperature info
temps = psutil.sensors_temperatures()

log_str="|"

# The var temps contains the following dictionary
# {'cpu_thermal': [shwtemp(label='', current=43.816, high=None, critical=None)]}
# to get the current temp, use the command
current_temp = temps["cpu_thermal"][0].current
#print("CPU_current_temp=%s" % current_temp)
log_str += "CPU_current_temp_C=%s" % current_temp + ";"

# this command evaluates the average CPU ussage after 1 second in Percent
cpu_avg_usage = psutil.cpu_percent(interval=0.5)
#print("CPU_avg_usage=%s" % cpu_avg_usage)
log_str += "CPU_avg_usage_percent=%s" % cpu_avg_usage + ";"

core_usage = psutil.cpu_percent(interval=0.5, percpu=True)
#print("Core_usages=%s" % core_usage)
log_str += "Core_usages_percent=%s" % core_usage + ";"

core_count = psutil.cpu_count()
#print("Number_of_cores=%s" % core_count)
log_str += "Number_of_cores=%s" % core_count + ";"

cpu_freq = psutil.cpu_freq()
#print("CPU_frequency_min=%s" % cpu_freq.min)
#print("CPU_frequency_max=%s" % cpu_freq.max)
#print("CPU_frequency_current=%s" % cpu_freq.current)
log_str += "CPU_frequency_min_MHz=%s" % cpu_freq.min + ";"
log_str += "CPU_frequency_max_MHz=%s" % cpu_freq.max + ";"
log_str += "CPU_frequency_current_MHz=%s" % cpu_freq.current + ";"


ram_total = psutil.virtual_memory().total
ram_available = psutil.virtual_memory().available
ram_usage = ram_total - ram_available
#print("RAM_total_byte=%s" % ram_total)
#print("RAM_available_byte=%s" % ram_available)
#print("RAM_usage_byte=%s" % ram_usage)
log_str += "RAM_total_byte=%s" % ram_total + ";"
log_str += "RAM_available_byte=%s" % ram_available + ";"
log_str += "RAM_usage_byte=%s" % ram_usage + ";"


# divide by 2**10 for KB
# divide by 2**20 for MB
# divide by 2**30 for GB
#example: hdd_total = hdd.total // (2**10)
hdd = psutil.disk_usage('/')
hdd_total = hdd.total
hdd_used = hdd.used
hdd_free = hdd.free
#print("HDD_total=%s" % hdd_total)
#print("HDD_used=%s" % hdd_used)
#print("HDD_free=%s" % hdd_free)
log_str += "HDD_total_byte=%s" % hdd_total + ";"
log_str += "HDD_used_byte=%s" % hdd_used + ";"
log_str += "HDD_free_byte=%s" % hdd_free + ";"


myLog.info(log_str)