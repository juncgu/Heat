#policy: solarBudget.py
#        provide method to get the real solar budget
#        when MPPT status is floating, Absorbing...
import time
import globalValue
import sys
sys.path.append(globalValue.top_path())
from datacollector import data_collect
from commit import commit_analysis
#method to get real solar budget
# with input: dataset
def get_solar_budget(dataset):
    '''
    when solar exceed, we need to get the real solar budget
    '''
    real_budget = dataset.outback['solarPower']
    stored_port_status = list(dataset.ipdu['status'])
    print "stored_port_status", stored_port_status 
    
    open_port = list(globalValue.ipdu_green_port())
    commit_analysis.ipdu_open_analysis(open_port)
    time.sleep(globalValue.solar_budget_sleep_time()) 
    close_port = list(globalValue.ipdu_utility_port()) 
    commit_analysis.ipdu_close_analysis(close_port)     
    time.sleep(globalValue.solar_budget_sleep_time()) 

    newdata = data_collect.DataCollection()
    newdata.get_ipdu_outback()
    
    if newdata.outback['solarPower'] > real_budget:
        real_budget = newdata.outback['solarPower']

    re_open_port = []
    re_close_port = []
    for i in range(len(stored_port_status)):
        if stored_port_status[i] == 0:
            re_close_port.append(i)
        elif stored_port_status[i] == 1:
            re_open_port.append(i)
    commit_analysis.ipdu_open_analysis(re_open_port)
    time.sleep(globalValue.solar_budget_sleep_time()) 
    commit_analysis.ipdu_close_analysis(re_close_port)        
   
    return real_budget


#method to get real solar budget
# without any input, it will get the dataset by itself
def get_solar_budget2():
    '''
    when solar exceed, we need to get the real solar budget
    '''
    dataset = data_collect.DataCollection()
    dataset.get_ipdu_outback()
    real_budget = dataset.outback['solarPower']
    stored_port_status = list(dataset.ipdu['status'])
    print "stored_port_status", stored_port_status 
    
    open_port = list(globalValue.ipdu_green_port())
    commit_analysis.ipdu_open_analysis(open_port)
    time.sleep(globalValue.solar_budget_sleep_time()) 
    close_port = list(globalValue.ipdu_utility_port()) 
    commit_analysis.ipdu_close_analysis(close_port)     
    
    time.sleep(globalValue.solar_budget_sleep_time()) 
    newdata = data_collect.DataCollection()
    newdata.get_ipdu_outback()
    
    if newdata.outback['solarPower'] > real_budget:
        real_budget = newdata.outback['solar_Power']

    re_open_port = []
    re_close_port = []
    for i in range(len(stored_port_status)):
        if stored_port_status[i] == 0:
            re_close_port.append(i)
        elif stored_port_status[i] == 1:
            re_open_port.append(i)
    commit_analysis.ipdu_open_analysis(re_open_port)
    commit_analysis.ipdu_close_analysis(re_close_port)        
   
    return real_budget
   
