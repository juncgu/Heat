#datacollector: sys_stats.py
#Description  : this class holds some overview-system level-longterm-statistics
#               different from data_collect, which is generated in every loop, the object of
#               this class walks through the whole progress. 
#Items:         1. ipdu switch counter
#               2. policy counter
import sys, os, time
import path
sys.path.append(path.upper_path())
from policy import globalValue

class SysStats:
    #1. ipdu switch counter
    ipdu_switch_counter = [[0,0,0,0,0,0,0,0]
                          ]

    #2. policy counter
    # policy 1,2
    policy_counter = {'max_green':0,
                      'solar_fluctuate':0,
                      'current_policy':0
                     }
    

    #functions:
    # init
    def __init__(self):
        pass

    # renew ipdu switch counter
    def add_ipdu_singleport(self, port, count): #e.g.(5, 1)
        if ((port > 7) or (port < 0)):
            print "SysStats->add_ipdu_singleport: wrong port number"
            return
        self.ipdu_switch_counter[0][port] += count 
    def add_ipdu_allport(self, all_list):  # e.g. ([0,0,0,1,1,2,1,0])
        if len(all_list) != 8:
            print "SysStats->add_ipdu_allport: wrong list len!"
            return 
        for i in range(0,8):
            self.ipdu_switch_counter[0][i] += all_list[i]
    def add_ipdu_changedport(self, port_list): #e.g. ([4,2,6]) this is single change
        for i in port_list:
            if ((i<=7) and (i>=0)):
                self.ipdu_switch_counter[0][i] += 1
            else:
                print "SysStats->add_ipdu_changedport: wrong port!"
                return 
        


    # renew policy counter
    # max_green: 1,    solar_fluctuate:2
    def add_policy(self, policy):
        if policy == 'max_green':
            self.policy_counter['max_green'] = self.policy_counter['max_green'] + 1
            self.policy_counter['current_policy'] = 1
        elif policy == 'solar_fluctuate':
            self.policy_counter['solar_fluctuate'] = self.policy_counter['solar_fluctuate'] + 1
            self.policy_counter['current_policy'] = 2
        else:
            print "SysStats->add_policy: no such policy !", policy

  
