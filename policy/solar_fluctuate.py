#policy: solar_fluctuate.py
#       solar energy supply fluctuate physical servers
import globalValue, solarBudget
import sys, signal, time
sys.path.append(globalValue.top_path())
from datacollector import data_collect
from commit import commit_analysis
from commit import cpufreq_dvfs
from commit import ipdu_switch
from commit import vm_migration


def solar_fluctuate_utility(data_set, syslog, ipdu_switch_count, statset):
    print 'Battery voltage is too low...'
    dataset = data_set
    dataset.outback['mpptStatus_str'] = 'solar_fluctuate_utility'
    close_port = globalValue.ipdu_green_port()
    open_port = globalValue.ipdu_utility_port()
    commit_analysis.ipdu_open_analysis(open_port)
    commit_analysis.ipdu_close_analysis(close_port)      
    
    #sys log
    one_log = ''
    time_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
    ong_log = one_log + time_stamp + ' solar_fluctuate_utility' 
    ipdu_power = ''
    ipdu_status = ''
    for i in dataset.ipdu['power']:
        ipdu_power = ipdu_power + ' ' + str(i)
    for j in dataset.ipdu['status']:
        ipdu_status = ipdu_status + ' ' + str(j)
    outback_data = ' '+str(dataset.outback['solarPower'])+' '+str(dataset.outback['mpptStatus'])+' '+str(dataset.outback['batteryCurrent'])+' '+str(dataset.outback['batteryVoltage'])+' '+str(dataset.outback['batterySoc'])+' '
    one_log = one_log + ipdu_status + ' ' + ipdu_power + ' ' + outback_data + ' ' + 'solar_fluctuate_utility'
    ipdu1 = ''
    ipdu2 = ''
    vm_str = ''
    dvfs_str = ''
    ipduopcode = ['o','o','o','o','c','c','c','c']    #n=none, c=close, o=open
    for i in range(0,4):
        ipdu_switch_count[i] += 1
    for i in range(4,8):
        ipdu_switch_count[i] += 1

    for i in ipduopcode:
        ipdu1 = ipdu1 + ' ' + i
    for j in ipdu_switch_count:
        ipdu2 = ipdu2 + ' ' + str(j) 
    one_log = one_log + ' '+ ipdu1 + ' ' + ipdu2 + ' ' + vm_str + ' ' + dvfs_str + '\n'
    sys_log_fd = open(syslog, 'a')
    sys_log_fd.write(one_log)
    sys_log_fd.close()
    #sys_stat
    statset.add_ipdu_changedport(open_port)
    statset.add_ipdu_changedport(close_port) 

    return 0


def solar_fluctuate(data_set, syslog, ipdu_switch_count, idle_count, statset):
    '''
    Put the fluctuate servers to green ports, 
    as long as solar power matches server power (in average)
    '''
    #get server fluctuate ratio list    server_flu_list
    #    server average power    server_average_list
    #    solar average power     solar_average
    dataset = data_set 
    dataset.outback['mpptStatus_str'] = 'solar_fluctuate'
    if dataset.outback['batteryVoltage_average'] < globalValue.battery_voltage_down():
        close_port = globalValue.ipdu_green_port()
        open_port = globalValue.ipdu_utility_port()
        commit_analysis.ipdu_open_analysis(open_port)
        commit_analysis.ipdu_close_analysis(close_port)
        #sys log
        one_log = ''
        time_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
        ong_log = one_log + time_stamp + ' solar_fluctuate' 
        ipdu_power = ''
        ipdu_status = ''
        for i in dataset.ipdu['power']:
            ipdu_power = ipdu_power + ' ' + str(i)
        for j in dataset.ipdu['status']:
            ipdu_status = ipdu_status + ' ' + str(j)
        outback_data = ' '+str(dataset.outback['solarPower'])+' '+str(dataset.outback['mpptStatus'])+' '+str(dataset.outback['batteryCurrent'])+' '+str(dataset.outback['batteryVoltage'])+' '+str(dataset.outback['batterySoc'])+' '
        one_log = one_log + ipdu_status + ' ' + ipdu_power + ' ' + outback_data + ' ' + 'solar_fluctuate'
        ipdu1 = ''
        ipdu2 = ''
        vm_str = ''
        dvfs_str = ''
        ipduopcode = ['o','o','o','o','c','c','c','c']    #n=none, c=close, o=open
        for i in range(0,4):
            ipdu_switch_count[i] += 1
        for i in range(4,8):
            ipdu_switch_count[i] += 1

        for i in ipduopcode:
            ipdu1 = ipdu1 + ' ' + i
        for j in ipdu_switch_count:
            ipdu2 = ipdu2 + ' ' + str(j) 
        one_log = one_log + ' '+ ipdu1 + ' ' + ipdu2 + ' ' + vm_str + ' ' + dvfs_str + '\n'
        sys_log_fd = open(syslog, 'a')
        sys_log_fd.write(one_log)
        sys_log_fd.close()
        #sys_stat
        statset.add_ipdu_changedport(open_port)
        statset.add_ipdu_changedport(close_port) 
        return 0



    server_flu_list = []
    server_average_list = []
    solar_average = dataset.outback['solarPower_average'] + 130
    for i in dataset.server['hostname']:
        server_flu_list.append(dataset.ipdu['port'][i]['var'])
        server_average_list.append(dataset.ipdu['port'][i]['average'])
   

    #figure out the fluctuate ratio ----map----- hostname
    sorted_server_flu = sorted(server_flu_list)
    server_flu_mapping = []
    bitmap = [0 for i in range(len(server_flu_list))]
    for i in range(len(sorted_server_flu)):
        for j in range(len(dataset.server['hostname'])):
            if server_flu_list[j] == sorted_server_flu[i]:
                if bitmap[j] == 0:
                    server_flu_mapping.append(j)
                    bitmap[j] = 1
                    break
    
    #start to arrange solar, according to their average power             
    solar_server = []
    for i in server_flu_mapping:
        if solar_average >= server_average_list[i]:    #solar is enough to handle this flu_server
            solar_server.append(dataset.server['hostname'][i])
            solar_average -= server_average_list[i]
    if solar_server == []:
        idle_count[0] = idle_count[0] + 1
    else:
        idle_count[0] = 0        
    

    #analyze and convert switching 
    close_port = []
    open_port = []
    for i in dataset.server['hostname']:
        if dataset.ipdu['port'][i]['status'] == 'g':   #'green' server
            if i in solar_server:
                pass
            else:    #change to u: close g and open u
                close_port.append(dataset.ipdu['port'][i]['g'][0])
                open_port.append(dataset.ipdu['port'][i]['u'][0])
        elif dataset.ipdu['port'][i]['status'] == 'm':    #'mix' server
            if i in solar_server:    #change to g: close u
                close_port.append(dataset.ipdu['port'][i]['u'][0])
            else:    #change to u: close g
                close_port.append(dataset.ipdu['port'][i]['g'][0])
        elif dataset.ipdu['port'][i]['status'] == 'u':    #'utility' server
            if i in solar_server:    # change to g: close u, open g
                close_port.append(dataset.ipdu['port'][i]['u'][0])
                open_port.append(dataset.ipdu['port'][i]['g'][0])
            else:
                pass
   
    #sys log
    one_log = ''
    time_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
    one_log = one_log + 'solar_fluctuate ' + time_stamp + ' '
    one_log = one_log + str(server_flu_list) + ' ' + str(server_average_list) + ' ' + str(solar_average) + ' ' + str(solar_server) + ' ' + str(open_port) + ' ' + str(close_port) + '\n' 
    sys_log_fd = open(syslog, 'a')
    sys_log_fd.write(one_log)
    sys_log_fd.close()

 
    #execute
    print 'server_flu_mapping: ', server_flu_mapping
    print 'solar_server: ', solar_server
    print 'close_port: ', close_port
    print 'open_port: ', open_port
    commit_analysis.ipdu_open_analysis(open_port)
    commit_analysis.ipdu_close_analysis(close_port)
    if (open_port != []):
        statset.add_ipdu_changedport(open_port)
    if (close_port != []):
        statset.add_ipdu_changedport(close_port)


