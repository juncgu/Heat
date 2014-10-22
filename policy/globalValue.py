#policy: globalValue.py
#        define some global values in policy part

#max_green.py
import os


def max_green_interval():
    return 300    #max time interval is 5 min

#ipdu green port number[hardware define]
def ipdu_green_port():
    return [0,1,2,3]

#ipdu utility poirt number[hardware define]
def ipdu_utility_port():
    return [4,5,6,7]

# hmi data filter buffer length
def filter_buffer_len():
    return 15

# sleep time during max_sloar:get_solar_budget()
# sleep after ipdu_switch_commit, give enough time for system refresh
def solar_budget_sleep_time():
    return 5 

# used in data collection, the url of probes data
def data_probes_url():
#    return 'http://controller:5001/v1/probes/ipdu_port_a1/'
    return 'http://controller:5001/v1/probes/'

def data_vm_url():
    return 'http://controller:8774/v2/b7dfe9f69e3048b3a146c9fa05ce1405/os-hypervisors/'

def filter_file_name():
    ABS_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = ABS_path+'/filter_data.txt' 
    return file_name

# outback and ipdu device are also powered by green energy
def power_baseline():
    return 100

# hmi device ip address
def hmi_ip():
    return '10.10.100.110'

# relay names in on/off switch
def relay_on_list():
    return ['c_on', 'l_on', 's_on', 'sc_on', '4_on']

def relay_off_list():
    return ['c_off', 'l_on', 's_off', 'sc_off', '4_off']

# policy config filename:
def policy_cfg_name():
    return 'policy.cfg'
# policy list
def policy_list():
    return ['max_green', 'solar_fluctuate', 'continue']

# policy select: solar_var threshold
# for 0.5h
def solar_var_threshold():
    return 100.0
    #return 200.0

# lower than this, switch to utility 
def battery_voltage_down():
    return 24.5
# higher than this, means battery is ready
def battery_voltage_up():
    return 26

# Heat top level path   (should be changed when needed)
def top_path():
    return '/root/solar/Heat'
