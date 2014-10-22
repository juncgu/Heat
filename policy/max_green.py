#policy: max_green.py

import copy
import signal
import sys
import globalValue, solarBudget
import time
sys.path.append(globalValue.top_path())
from datacollector import data_collect, filterBuffer, sys_stats
from commit import commit_analysis
from commit import cpufreq_dvfs
from commit import ipdu_switch
from commit import vm_migration



def max_green(data_set, syslog, ipdu_switch_count, filter_buffer, statset):
    '''
    This is the main loop of maximum green policy
    '''
    #log files
#    ipdu_switch_count = [0,0,0,0,0,0,0,0]
    #datafilter: filterBuffer
#    filter_buffer = filterBuffer.filterBuffer(globalValue.filter_buffer_len())


    #step1: data collector
    dataset = data_set
    dataset.get_vm_info()
    
    commit_dict = {}    
    one_log = '' 
    time_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time())) 
    one_log = one_log + time_stamp + ' max_green '
    ipdu_power = ''
    ipdu_status = ''
    function = ''
    for i in dataset.ipdu['power']:
        ipdu_power = ipdu_power + ' ' + str(i)
    for j in dataset.ipdu['status']:
        ipdu_status = ipdu_status + ' ' + str(j)
    outback_data = ' '+str(dataset.outback['solarPower'])+' '+str(dataset.outback['mpptStatus'])+' '+str(dataset.outback['batteryCurrent'])+' '+str(dataset.outback['batteryVoltage'])+' '+str(dataset.outback['batterySoc'])+' '
    one_log = one_log + ipdu_status + ' ' + ipdu_power + ' ' + outback_data 

    #Juncheng Gu  Sep1 
    #filter data
    #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>enter filter>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    #dataset.data_filter(filter_buffer)
    #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>leave filter>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        
    #step2: max_green algorithm process
    if (dataset.outback['mpptStatus'] == 3):   
        print ">>>Policy:max green: MPPT Status is Absorb ..."
        # Solar_excess  
        commit_dict = solar_excess(dataset)
        dataset.outback['mpptStatus_str'] = 'Absorb'
        function = 'Absorb:solar_execess'
    elif (dataset.outback['mpptStatus'] == 2):        
        print ">>>Policy:max green: MPPT Status is Bulk ..."
        # Solar_starve  
#       commit_dict = solar_starve(dataset)
        dataset.outback['mpptStatus_str'] = 'Bulk'
        commit_dict = mppt_bulk(dataset)
        function = 'Bulk:mppt_bulk'
    elif (dataset.outback['mpptStatus'] == 1):
        print ">>>Policy:max green: MPPT Status is Float ..."
        if (dataset.outback['batteryCurrent'] > 0):
            print ">>>Policy:max green: MPPT status is Floating..."
            dataset.outback['mpptStatus_str'] = 'Floating'
            commit_dict = solar_excess(dataset)
            function = 'Floating:solar_excess'
        elif (dataset.outback['batteryCurrent'] < 0):
            print ">>>Policy:max green: MPPT status is MPPT Float..."
            dataset.outback['mpptStatus_str'] = 'MPPT Float'
            commit_dict = solar_starve(dataset)
            function = 'MPPT Float:solar_starve'
    elif (dataset.outback['mpptStatus'] == 0):
        print ">>>Policy:max green: MPPT Status is Silent ..."
        dataset.outback['mpptStatus_str'] = 'Silent'
        commit_dict = {}
        function = 'Silent'
    elif (dataset.outback['mpptStatus'] == 4):
        dataset.outback['mpptStatus_str'] = 'EQ'
        print ">>>Policy:max green: MPPT Status is EQ ..."
        commit_dict = {}
        function = 'EQ'
    else:
        print ">>>Policy:max green: MPPT Status is abnormal ..."
        dataset.outback['mpptStatus_str'] = 'abnormal'
        commit_dict = {}
        function = 'abnormal'
    #step3: commit
    commit_analysis.commit_analysis_execute(commit_dict)
    #commit log
    ipdu1 = ''
    ipdu2 = ''
    vm_str = ''
    dvfs_str = ''
    ipduopcode = ['n','n','n','n','n','n','n','n']    #n=none, c=close, o=open
    if ((commit_dict != {}) and (commit_dict['open_port'] != [])): 
        for i in commit_dict['open_port']:
            ipduopcode[i] = 'o'
            ipdu_switch_count[i] += 1
    if ((commit_dict != {}) and (commit_dict['close_port'] != [])): 
        for j in commit_dict['close_port']:
            ipduopcode[j] = 'c' 
            ipdu_switch_count[j] += 1
    for i in ipduopcode:
        ipdu1 = ipdu1 + ' ' + i
    for j in ipdu_switch_count:
        ipdu2 = ipdu2 + ' ' + str(j) 
    if (commit_dict != {}):
        vm_str = ' '+str(commit_dict['vm_migration'])+' '
    if (commit_dict != {}):
        dvfs_str = ' '+str(commit_dict['revoke_dvfs'])+' '
    one_log = one_log + ' '+ function +' '+ ipdu1 + ' ' + ipdu2 + ' ' + vm_str + dvfs_str + '\n'
    sys_log_fd = open(syslog, 'a')
    sys_log_fd.write(one_log)
    sys_log_fd.close()

    #sysstat
    if ((commit_dict != {}) and (commit_dict['open_port'] != [])): 
        statset.add_ipdu_changedport(commit_dict['open_port'])
    if ((commit_dict != {}) and (commit_dict['close_port'] != [])): 
        statset.add_ipdu_changedport(commit_dict['close_port']) 


def get_solar_budget(dataset):
    '''
    When solar_excess, we needs to get the real solar budget
    '''
    real_budget = dataset.outback['solarPower']
    stored_port_status = list(dataset.ipdu['status'])    #record formal port status
    #test
    print "stored_port_status", stored_port_status
    #Step1: get server power and sorted in sequence
    server_power = []
    for i in globalValue.ipdu_green_port():
         server_power.append(dataset.ipdu['power'][i] + dataset.ipdu['power'][i+4]) 
    print "server_power", server_power
    sorted_power = sorted(server_power, reverse = True)    # large---small 
    sorted_server_map = []    # mapping sorted---server
    server_bitmap = [0 for i in range(len(sorted_power))]    #record if the server has been mapped
    # get sorted--server mapping relation        
    for i in range(len(sorted_power)):
        for j in range(len(server_power)):
            if ((sorted_power[i] == server_power[j]) and (server_bitmap[j] == 0)) :
                sorted_server_map.append(j) 
                server_bitmap[j] = 1
                break
    #test
    print "sorted_server", sorted_power
    print "mapping...", sorted_server_map 

    #Step2: switch to utility
    tmp = [1,1,1,1,2,2,2,2]

    ipdu_switch.ipdu_switch_commit(tmp)

    #Step3: get closer to solar budget
    #       compare the old solarPower and new One
    newset = data_collect.DataCollection()
    old_solarPower = 0 

    i = 0
    for i in range(len(sorted_power)):
        tmp_opcode = [0,0,0,0,0,0,0,0]
        tmp_opcode[sorted_server_map[i]] = 2
        tmp_opcode[sorted_server_map[i]+4] = 1
        print tmp_opcode
        ipdu_switch.ipdu_switch_commit(tmp_opcode)
        print "Sleeping waiting for ipdu switch..."
        time.sleep(globalValue.solar_budget_sleep_time())
        '''
        retrieve newset dataset: newset
        '''
        newset.get_ipdu_outback()
        green_provide = 0
        for j in globalValue.ipdu_green_port():    #green power should provide
            green_provide += newset.ipdu['power'][j]

        if (((newset.outback['solarPower'] - old_solarPower) < sorted_power[i]/2) or (newset.outback['solarPower'] <= green_provide)):
            print ">>>>Get the real solar budget:", newset.outback['solarPower'] 
            real_budget = newset.outback['solarPower']
            break
        else:
            old_solarpower = newset.outback['solarPower']
            real_budget = newset.outback['solarPower']
                    
#test
#        newset.outback['solarPower'] = 600 
#        newset.ipdu['power'][i] = server_power[sorted_server_map[i]]/2 
#        print "new add green port power", server_power[sorted_server_map[i]]/2       


#bug
#        green_provide = 0
#        for j in globalValue.ipdu_green_port():    #green power should provide
#            green_provide += newset.ipdu['power'][j]
#        print "green_provide", green_provide
        
#        if newset.outback['solarPower'] < green_provide: 
#            print ">>>>>>>>>>>solar is lower than green_provided"
#            real_budget = newset.outback['solarPower'] 
#            break
  
    #Step4: retrieve solar budget
    retrieve_opcode = [0,0,0,0,0,0,0,0]
    for i in range(len(stored_port_status)):
        if stored_port_status[i] == 0:
            retrieve_opcode[i] = 1
        elif stored_port_status[i] == 1:
            retrieve_opcode[i] = 2
    print "stored_port_status", stored_port_status
    print "retrieve_opcode", retrieve_opcode
    ipdu_switch.ipdu_switch_commit(retrieve_opcode) 
    
    return real_budget



def solar_excess(dataset):

    commit_dict = {}
    commit_dict['open_port'] = []    #[0,1,2,3]
    commit_dict['close_port'] = []    #[4,5,6,7]
    commit_dict['revoke_dvfs'] = {}    #{'compute1':new_freq, 'compute2':new_freq}
    commit_dict['vm_migration'] = []    #[{'src':'compute1', 'dest':'compute2', 'vmid':id}] 

    #if batteryVoltage < threshold, then no actions
    if dataset.outback['batteryVoltage'] < 25.0:
        print "Battery Voltage too low, take no actions"
        return commit_dict

    # to judge whether need to test solar budget
    h_time = time.strftime('%H', time.localtime(time.time()))
    afternoon = ['13', '14', '15', '16', '17', '18', '19', '20']
    no_action_status = ['MPPT Float', 'Bulk']

    #Step1: get real solar_budget
    if ((h_time in afternoon) and (dataset.outback['last_mpptStatus'] in no_action_status)):
        real_solar = dataset.outback['last_solarPower']
    else:
        real_solar = solarBudget.get_solar_budget(dataset)

    print ">>>>>>>>>>solar excess: real_solar_budget:", real_solar    
    time.sleep(10)
    #Step2: retrieve key information    
    # have been done and retrieved in dataset
    solar_using = 0
    dataset.get_ipdu_outback()
    for i in globalValue.ipdu_green_port():
        solar_using += dataset.ipdu['power'][i] 
    solar_over = real_solar - solar_using
    print ">>>>>>solar excess: solar_over: ", solar_over
    if solar_over <= 0:    # if solar_excess is an error
        return commit_dict   
#test    
#    solar_over = 300

    #Copy port status for intermediate process
    tmp_port_status = copy.copy(dataset.ipdu['port'])
    print "tmp_port_status: ", tmp_port_status
    #Step3: Calculate Policy
    #  3.1: open green port
    open_green_list = []
    close_utility_list = []
    for i in dataset.domain['greenPool']:    #get green-prefered-server 
        print ">>>>>>>greenPool:", i
        if (tmp_port_status[i]['g'][1] == 0 and tmp_port_status[i]['u'][1] == 1):    # current: utility
            if solar_over >= dataset.ipdu['power'][tmp_port_status[i]['u'][0]]:    #switch to pure green
                solar_over = solar_over - dataset.ipdu['power'][tmp_port_status[i]['u'][0]]      
                open_green_list.append(tmp_port_status[i]['g'][0])    #record the open_green port
                close_utility_list.append(tmp_port_status[i]['u'][0])    # record the close_utility port
                tmp_port_status[i]['g'][1] = 1    #update tmp_port_status
                tmp_port_status[i]['u'][1] = 0
            elif solar_over >= dataset.ipdu['power'][tmp_port_status[i]['u'][0]]/2:    #switch to mix
                solar_over = solar_over - dataset.ipdu['power'][tmp_port_status[i]['u'][0]]/2      
                open_green_list.append(tmp_port_status[i]['g'][0])    
                tmp_port_status[i]['g'][1] = 1
        elif (tmp_port_status[i]['g'][1] == 1 and tmp_port_status[i]['u'][1] == 1):    # current: mix
            if solar_over >= dataset.ipdu['power'][tmp_port_status[i]['u'][0]]:    #switch to pure green
                solar_over = solar_over - dataset.ipdu['power'][tmp_port_status[i]['u'][0]]      
                close_utility_list.append(tmp_port_status[i]['u'][0])    # record the close_utility port
                tmp_port_status[i]['u'][1] = 0
        else:    #current: pure green
            continue 
   
    if solar_over <= 0:
        return commit_dict
    for j in dataset.server['hostname']:     #hosts not in greenPool
        if j != dataset.domain['greenPool']:
            if ((tmp_port_status[j]['g'][1] == 0) and (tmp_port_status[j]['u'][1] == 1)):    #utility host
                if solar_over >= dataset.ipdu['power'][tmp_port_status[j]['u'][0]]:    #switch to g host
                    solar_over = solar_over - dataset.ipdu['power'][tmp_port_status[j]['u'][0]] 
                    close_utility_list.append(tmp_port_status[j]['u'][0])
                    open_green_list.append(tmp_port_status[j]['g'][0])
                    tmp_port_status[j]['u'][1] = 0
                    tmp_port_status[j]['g'][1] = 1
                elif solar_over >= dataset.ipdu['power'][tmp_port_status[j]['u'][0]]/2:    #switch to mix host
                    solar_over = solar_over - dataset.ipdu['power'][tmp_port_status[j]['u'][0]]/2
                    open_green_list.append(tmp_port_status[j]['g'][0])   
                    tmp_port_status[j]['g'][1] = 1
            elif ((tmp_port_status[j]['g'][1] == 1) and (tmp_port_status[j]['u'][1] == 1)):    #mix host
                if solar_over >= dataset.ipdu['power'][tmp_port_status[j]['u'][0]]:    #switch to u host
                    solar_over = solar_over - dataset.ipdu['power'][tmp_port_status[j]['u'][0]]
                    close_utility_list.append(tmp_port_status[j]['u'][0])
                    tmp_port_status[j]['u'][1] = 0
            else:
                continue
 
    #test
    print "open_green_list: ", open_green_list
    print "close_utility_list: ", close_utility_list
    print "solar_over after open green port: ", solar_over
    commit_dict['open_port'] = copy.copy(open_green_list)    #[0,1,2,3]
    commit_dict['close_port'] = copy.copy(close_utility_list)    #[4,5,6,7]  
 
    if solar_over <= 0:
        return commit_dict
    #  3.2: Revoke DVFS
    revoke_dict = {}    #revoke dvfs according to revoke_list
    for i in dataset.domain['dvfsPool']:
        dvfs_host = dataset.server['dvfs'][i]
        if dvfs_host['current'] < dvfs_host['min']:      #  current < min : error
            continue
        elif dvfs_host['current'] >= dvfs_host['max']:   #  current >= max: no dvfs
            continue
        else:                                            #  min <= current < max
            cur_scale = dvfs_host['cur_scale'] 
        for j in range(cur_scale, len(dvfs_host['power'])):    #add dvfs_host's DVFS scale power
            if ((tmp_port_status[i]['g'][1] == 1) and (tmp_port_status[i]['u'][1] == 0)):    #green host
                if solar_over >= dvfs_host['power'][j]:
                    revoke_dict[i] = dvfs_host['scale'][j+1]
                    solar_over = solar_over - dvfs_host['power'][j]
                else:
                    break
            elif ((tmp_port_status[i]['g'][1] == 1) and (tmp_port_status[i]['u'][1] == 1)):    #mix host    
                if solar_over >= dvfs_host['power'][j]/2:
                    revoke_dict[i] = dvfs_host['scale'][j+1]
                    solar_over = solar_over - dvfs_host['power'][j]/2 
                else:
                    break
    #test
    print "revoke_dict", revoke_dict   
    print "solar_over after open revoke", solar_over
    commit_dict['revoke_dvfs'] = copy.copy(revoke_dict)    #{'compute1':new_freq, 'compute2':new_freq}


    if solar_over <= 0:
        return commit_dict
    #  3.3: VM migration
    green_list = []
    utility_list = []
    mix_list = []
    migrate_list = []
    #     classify
    for i in dataset.domain['vmmigrationPool']:
        if ((tmp_port_status[i]['g'][1]==1) and (tmp_port_status[i]['u'][1]==1)):    #g+u
            mix_list.append(i)
        elif ((tmp_port_status[i]['g'][1]==1) and (tmp_port_status[i]['u'][1]==0)):    #g         
            green_list.append(i) 
        elif ((tmp_port_status[i]['g'][1]==0) and (tmp_port_status[i]['u'][1]==1)):    #u
            utility_list.append(i)
    #test
    print "green_list:", green_list
    print "utility_list:", utility_list
    print "mix_list:", mix_list

    #     from u to mix/g
    for j in utility_list:
        utility_host = dataset.server['vm'][j]
        if utility_host['left'] >= utility_host['count']:    #no vm on this host
            continue
        else:
            for k in utility_host['vm']:    
                if (k['power'] <= solar_over):                        #solar_over > vm power
                    for n in green_list:                             # select a green host 
                        if dataset.server['vm'][n]['left'] >= 1:
                            solar_over = solar_over - k['power']
                            migrate_list.append({'src':j, 'dest':n, 'vmid':k['id']})
                            break
                elif (k['power']/2 <= solar_over):                   #solar_over > vmpower/2
                    for m in mix_list:
                        if dataset.server['vm'][m]['left'] >=1:     #select a mix host
                            solar_over = solar_over - k['power']/2
                            migrate_list.append({'src':j, 'dest':m, 'vmid':k['id']})
                            break
    #test
    print "migrate_list after u--mix/g:", migrate_list
    print "solar_over:", solar_over

    #     from mix to g
    for a in mix_list:
        mix_host = dataset.server['vm'][a]
        if mix_host['left'] >= mix_host['count']:    # no vm on this host
            continue
        else:
            for b in mix_host['vm']:
                if(b['power']/2 <= solar_over):
                    for c in green_list:
                        if dataset.server['vm'][c]['left'] >= 1:
                            solar_over = solar_over - b['power']/2
                            migrate_list.append({'src':a, 'dest':c, 'vmid':b['id']})
                            break
    #test
    print "migrate_list after mix--g:", migrate_list
    print "solar_over:", solar_over

    #prepare for return
    commit_dict['vm_migration'] = copy.copy(migrate_list)    #[{'src':'compute1', 'dest':'compute2', 'vmid':id}] 
    print commit_dict
    return commit_dict



def solar_starve(dataset):
    '''
    when solar is not enough, compared with the using solar power
    '''
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Enter solar_starve>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    commit_dict = {}
    commit_dict['open_port'] = []    #[0,1,2,3]
    commit_dict['close_port'] = []    #[4,5,6,7]
    commit_dict['revoke_dvfs'] = {}    #{'compute1':new_freq, 'compute2':new_freq}
    commit_dict['vm_migration'] = []    #[{'src':'compute1', 'dest':'compute2', 'vmid':id}] 

    #Copy port status for intermediate process
    tmp_port_status = copy.copy(dataset.ipdu['port'])

    #Step1: retrieve key information    
    # have been done and retrieved in dataset  
    solar_using = 0
    for i in globalValue.ipdu_green_port():
        solar_using += dataset.ipdu['power'][i] 
    solar_lack = solar_using + globalValue.power_baseline() - dataset.outback['solarPower']
    if solar_lack <= 0:    # if solar_starve is an error
        print ">>>>>>>>>>>>>>>>>>>>>>solar starve: solar_lack < 0, error", solar_using, dataset.outback['solarPower']
        return commit_dict    

    #    2.1: deploy DVFS
    deploy_dict = {}
    for i in dataset.domain['dvfsPool']:
        dvfs_host = dataset.server['dvfs'][i]
        if dvfs_host['current'] < dvfs_host['min']:
            continue
        elif dvfs_host['current'] >= dvfs_host['max']:
            continue
        else:
            cur_scale = dvfs_host['cur_scale']
        for j in range(cur_scale, len(dvfs_host['power'])):
            if ((tmp_port_status[i]['g'][1] == 1) and (tmp_port_status[i]['u'][1] == 0)):    #green host
                if solar_lack >= dvfs_host['power'][j]:
                    deploy_dict[i] = dvfs_host['scale'][j+1]
                    solar_lack = solar_lack - dvfs_host['power'][j]
                else:
                    break
            elif ((tmp_port_status[i]['g'][1] == 1) and (tmp_port_status[i]['u'][1] == 1)):    #mix host    
                if solar_lack >= dvfs_host['power'][j]/2:
                    deploy_dict[i] = dvfs_host['scale'][j+1]
                    solar_lack = solar_lack - dvfs_host['power'][j]/2 
                else:
                    break
    commit_dict['revoke_dvfs'] = deploy_dict

    if solar_lack <= 0:
        return commit_dict

    #    2.2:close green port
    close_green_list = []
    open_utility_list = []
    for i in dataset.server['hostname']:     #hosts not in greenPool
        if solar_lack > 0:
            if i != dataset.domain['greenPool']:
                if ((tmp_port_status[i]['g'][1] == 1) and (tmp_port_status[i]['u'][1] == 0)):    #green host
                    if solar_lack >= dataset.ipdu['power'][tmp_port_status[i]['g'][0]]:    #switch to u host
                        solar_lack = solar_lack - dataset.ipdu['power'][tmp_port_status[i]['g'][0]] 
                        close_green_list.append(tmp_port_status[i]['g'][0])
                        open_utility_list.append(tmp_port_status[i]['u'][0])
                        tmp_port_status[i]['u'][1] = 1
                        tmp_port_status[i]['g'][1] = 0
                    elif solar_lack >= dataset.ipdu['power'][tmp_port_status[i]['g'][0]]/2:    #switch to mix host
                        solar_lack = solar_lack - dataset.ipdu['power'][tmp_port_status[i]['g'][0]]/2
                        open_utility_list.append(tmp_port_status[i]['u'][0])   
                        tmp_port_status[i]['u'][1] = 1
                elif ((tmp_port_status[i]['g'][1] == 1) and (tmp_port_status[i]['u'][1] == 1)):    #mix host
                    if solar_lack >= dataset.ipdu['power'][tmp_port_status[i]['g'][0]]:    #switch to u host
                        solar_lack = solar_lack - dataset.ipdu['power'][tmp_port_status[i]['g'][0]]
                        close_green_list.append(tmp_port_status[i]['g'][0])
                        tmp_port_status[i]['g'][1] = 0
                else:
                    continue
        else:
            break
     
    if solar_lack > 0:                           
        for j in dataset.domain['greenPool']:
            if ((tmp_port_status[j]['g'][1] == 1) and (tmp_port_status[j]['u'][1] == 0)):
                if solar_lack >= dataset.ipdu['power'][tmp_port_status[j]['g'][0]]:          
                    solar_lack = solar_lack - dataset.ipdu['power'][tmp_port_status[j]['g'][0]] 
                    close_green_list.append(tmp_port_status[j]['g'][0])
                    open_utility_list.append(tmp_port_status[j]['u'][0])
                    tmp_port_status[j]['u'][1] = 1
                    tmp_port_status[j]['g'][1] = 0
                elif solar_lack >= dataset.ipdu['power'][tmp_port_status[j]['g'][0]]/2:    #switch to mix host
                    solar_lack = solar_lack - dataset.ipdu['power'][tmp_port_status[j]['g'][0]]/2
                    open_utility_list.append(tmp_port_status[j]['u'][0])   
                    tmp_port_status[j]['u'][1] = 1
            elif ((tmp_port_status[j]['g'][1] == 1) and (tmp_port_status[j]['u'][1] == 1)):    #mix host
                if solar_lack >= dataset.ipdu['power'][tmp_port_status[j]['g'][0]]:    #switch to u host
                    solar_lack = solar_lack - dataset.ipdu['power'][tmp_port_status[j]['g'][0]]
                    close_green_list.append(tmp_port_status[j]['g'][0])
                    tmp_port_status[j]['g'][1] = 0
            else:
                continue
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>solar starve: open_port", open_utility_list
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>solar starve: close_port", close_green_list
    commit_dict['open_port'] = open_utility_list    #[0,1,2,3]
    commit_dict['close_port'] = close_green_list

    if solar_lack <= 0:
        return commit_dict
    #    2.3: vm migration
    green_list = []
    utility_list = []
    mix_list = []
    migrate_list = []
    #     classify
    for i in dataset.domain['vmmigrationPool']:
        if ((tmp_port_status[i]['g'][1]==1) and (tmp_port_status[i]['u'][1]==1)):    #g+u
            mix_list.append(i)
        elif ((tmp_port_status[i]['g'][1]==1) and (tmp_port_status[i]['u'][1]==0)):    #g         
            green_list.append(i) 
        elif ((tmp_port_status[i]['g'][1]==0) and (tmp_port_status[i]['u'][1]==1)):    #u
            utility_list.append(i)
    #test
    print "green_list:", green_list
    print "utility_list:", utility_list
    print "mix_list:", mix_list

    #     from g to mix/u
    for j in green_list:
        green_host = dataset.server['vm'][j]
        if green_host['left'] >= green_host['count']:    #no vm on this host
            continue
        else:
            for k in green_host['vm']:    
                if (k['power'] <= solar_lack):                        #solar_lack > vm power
                    for n in utility_list:                             # select a u host 
                        if dataset.server['vm'][n]['left'] >= 1:
                            solar_lack = solar_lack - k['power']
                            migrate_list.append({'src':j, 'dest':n, 'vmid':k['id']})
                            break
                elif (k['power']/2 <= solar_lack):                   #solar_over > vmpower/2
                    for m in mix_list:
                        if dataset.server['vm'][m]['left'] >=1:     #select a mix host
                            solar_lack = solar_lack - k['power']/2
                            migrate_list.append({'src':j, 'dest':m, 'vmid':k['id']})
                            break
    #test
    print "migrate_list after u--mix/g:", migrate_list
    print "solar_lack:", solar_lack

    #     from mix to g
    for a in mix_list:
        mix_host = dataset.server['vm'][a]
        if mix_host['left'] >= mix_host['count']:    # no vm on this host
            continue
        else:
            for b in mix_host['vm']:
                if(b['power']/2 <= solar_lack):
                    for c in utility_list:
                        if dataset.server['vm'][c]['left'] >= 1:
                            solar_lack = solar_lack - b['power']/2
                            migrate_list.append({'src':a, 'dest':c, 'vmid':b['id']})
                            break
    #prepare for return
    commit_dict['vm_migration'] = migrate_list    #[{'src':'compute1', 'dest':'compute2', 'vmid':id}] 
    return commit_dict


def mppt_bulk(dataset):
    '''
    batteryCurrent <0, then close some green port
    '''
    commit_dict = {}
    commit_dict['open_port'] = []    #[0,1,2,3]
    commit_dict['close_port'] = []    #[4,5,6,7]
    commit_dict['revoke_dvfs'] = {}    #{'compute1':new_freq, 'compute2':new_freq}
    commit_dict['vm_migration'] = []    #[{'src':'compute1', 'dest':'compute2', 'vmid':id}] 
    if dataset.outback['batteryCurrent'] > 0.0:
        return commit_dict

    #Copy port status for intermediate process
    close_green_list = []
    open_utility_list = []
    for j in dataset.server['hostname']:     #hosts not in greenPool
        if j != dataset.domain['greenPool']:
            if ((dataset.ipdu['port'][j]['g'][1] == 1) and (dataset.ipdu['port'][j]['u'][1] == 0)):    #green host
                close_green_list.append(dataset.ipdu['port'][j]['g'][0])
                open_utility_list.append(dataset.ipdu['port'][j]['u'][0])
                commit_analysis.ipdu_open_analysis(open_utility_list)
                commit_analysis.ipdu_close_analysis(close_green_list)            
            elif ((dataset.ipdu['port'][j]['g'][1] == 1) and (dataset.ipdu['port'][j]['u'][1] == 1)):    #mix host
                close_green_list.append(dataset.ipdu['port'][j]['g'][0])
                commit_analysis.ipdu_close_analysis(close_green_list) 
            else:    #utility host
                continue
        time.sleep(5)
        dataset.get_ipdu_outback()
        if dataset.outback['batteryCurrent'] > 0.0:
            return commit_dict

    close_green_list = []
    open_utility_list = []
    for i in dataset.domain['greenPool']:
        if ((dataset.ipdu['port'][j]['g'][1] == 1) and (dataset.ipdu['port'][j]['u'][1] == 0)):    #green host
            close_green_list.append(dataset.ipdu['port'][j]['g'][0])
            open_utility_list.append(dataset.ipdu['port'][j]['u'][0])
            commit_analysis.ipdu_open_analysis(open_utility_list)
            commit_analysis.ipdu_close_analysis(close_green_list)            
        elif ((dataset.ipdu['port'][j]['g'][1] == 1) and (dataset.ipdu['port'][j]['u'][1] == 1)):    #mix host
            close_green_list.append(dataset.ipdu['port'][j]['g'][0])
            commit_analysis.ipdu_close_analysis(close_green_list) 
        else:    #utility host
            continue 
        time.sleep(5)
        dataset.get_ipdu_outback()
        if dataset.outback['batteryCurrent'] > 0.0:
            return commit_dict

    print 'commit open_port: ', commit_dict['open_port']
    print 'commit close_port: ', commit_dict['close_port']
    print 'revoke_dvfs: ', commit_dict['revoke_dvfs']
    print 'commit vm_migration: ', commit_dict['vm_migration']
    return commit_dict



def loop_test():
    print globalValue.max_green_interval
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(globalValue.max_green_interval)
    print "Start..."
    while 1:
        print "IN WHILE LOOP"
        signal.pause()


if __name__ == "__main__":
    pass 
