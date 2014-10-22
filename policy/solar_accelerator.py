#policy: solar_accelerator
#prerequisit: workload < solar_budget
#      : when solar extras, use accelerate-knobs
#       1. send cmd to GPU
#       2. add hadoop node
import globalValue, solarBudget
import sys, os
sys.path.append(globalValue.top_path())
from datacollector import data_collect
from commit import commit_analysis
from commit import cpufreq_dvfs
from commit import ipdu_switch

def solar_accelerate():
    dataset = 

def GPU_accelerate():
    pass

def Hadoop_accelerate():
    pass



if __name__ == '__main__':
    pass
