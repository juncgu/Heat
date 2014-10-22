#datacollector
#use hmi

import sys
import os
import data_collect, sys_stats

def hmi_monitor(dataset, statset):
    ABS_path = os.path.split(os.path.realpath(__file__))[0]
    cmd = ABS_path + "/HMI_monitor "

    for i in range(0, 8):
        cmd = cmd + str(dataset.ipdu['power'][i]) + ' '

    cmd = cmd + str(dataset.outback['solarPower']) + ' '
    cmd = cmd + str(dataset.outback['batteryVoltage']) + ' '
    cmd = cmd + str(dataset.outback['batteryCurrent']) + ' '
    cmd = cmd + str(dataset.outback['batterySoc']) + ' '
    cmd = cmd + str(dataset.energy['solar_energy']) + ' '
    cmd = cmd + str(dataset.outback['solarPower_var']) + ' '
    cmd = cmd + str(dataset.energy['green_port_energy']) + ' '
    cmd = cmd + str(dataset.energy['brown_port_energy']) + ' '
    cmd = cmd + str(dataset.outback['mpptStatus']) + ' '
    cmd = cmd + str(dataset.hmi_filter['current1']) + ' '
    cmd = cmd + str(dataset.hmi_filter['current2']) + ' '

    for i in range(0,8):
        cmd = cmd + str(statset.ipdu_switch_counter[0][i]) + ' '    
    cmd = cmd + str(statset.policy_counter['max_green']) + ' '
    cmd = cmd + str(statset.policy_counter['solar_fluctuate']) + ' '
    cmd = cmd + str(statset.policy_counter['current_policy']) + ' '
    cmd = cmd + str(dataset.energy['roi']) + ' '
    cmd = cmd + str(dataset.energy['economic_benefit'])

    print cmd
    
    output = os.popen(cmd)


if __name__ == '__main__':
    dataset = data_collect.DataCollection()
    dataset.get_ipdu_outback()
    
    hmi_monitor(dataset, statset)
