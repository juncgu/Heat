#commit: hmi_relay.py
#        receive cmd from commit_analysis
#        execute and call ./hmi_relay
import path
import os
import sys
#upper_path = os.getcwd()[0:-7]
sys.path.append(path.upper_path())
from policy import globalValue

def hmi_relay_execute(relay_port):
    ABS_path = os.path.split(os.path.realpath(__file__))[0]
    ip = globalValue.hmi_ip()
    cmd = ABS_path + '/hmi_relay '+ ip
    relay_on_list = globalValue.relay_on_list()
    relay_off_list = globalValue.relay_off_list()
    switch_count = 0
    for i in range(len(relay_port)):
        if relay_port[i] == 1:
            cmd = cmd +' '+relay_on_list[i]
            switch_count += 1
        elif relay_port[i] == -1:
            cmd = cmd +' '+relay_off_list[i]
            switch_count += 1
        elif relay_port[i] == 0:
            pass
    if switch_count != 0:
        os.system(cmd)
    else:
        print "relay_ctl: nothing to execute"
     

