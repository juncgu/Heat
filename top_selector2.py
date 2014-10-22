#Heat: top_selector
#      select the top policy for accuracy
#      current policy : max_green solar_fluctuate
import sys, os, signal, time, copy
from policy import max_green, solar_fluctuate, globalValue, emergency 
from datacollector import filterBuffer, data_collect, hmi_monitor, sys_stats

def alarm_handler(signum, frame):    #arguments are essential
    '''
    Alarm Handler
    time interval from globalValue.max_green_interval()
    '''
    print "Enter alarm handler!"
    signal.alarm(globalValue.max_green_interval())


def main_loop():
    '''
    loop work
    ''' 
    #prepare for init alarm
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(globalValue.max_green_interval())
   
    #policy name
    policy_name = ''
    try:
        cfg_fd = open(globalValue.policy_cfg_name(), 'r')
        i = cfg_fd.readlines(1)
        cfg_fd.close()
        policy_name = i[0].strip('\n')
    except:
        print "Error: policy.cfg "
    print policy_name        
    last_policy = policy_name
    #loop judgement 
    loop_token = True
    if (policy_name in globalValue.policy_list()):
        loop_token = True
    else:
        loop_token = False

    # sys log
    cwd = os.getcwd() 
    time_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
    sys_log = cwd + '/' + time_stamp + '.txt'   
    policy_log = cwd + '/' + time_stamp + '_policy.txt'
    print sys_log

    #max_green parameter
    ipdu_switch_count = [0,0,0,0,0,0,0,0]
    filter_buffer = filterBuffer.filterBuffer(globalValue.filter_buffer_len())
  
    #solar_fluctuate
    idle_count = [0]


    # sys_stats 
    statset = sys_stats.SysStats()
 

    # another select mechanism
    last_mpptStatus = ''   
    last_solarPower = 0
    while loop_token:
        dataset = data_collect.DataCollection()
        dataset.get_ipdu_outback()
        dataset.data_filter(filter_buffer)
        dataset.outback['last_mpptStatus'] = last_mpptStatus
        dataset.outback['last_solarPower'] = last_solarPower
     

        #policy log 
        loop_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
        loop_log = loop_stamp
        if last_policy == 'max_green':
            if dataset.outback['solarPower_var'] > globalValue.solar_var_threshold():
                solar_fluctuate.solar_fluctuate(dataset, sys_log, ipdu_switch_count, idle_count, statset)
                statset.add_policy('solar_fluctuate')
                last_mpptStatus = dataset.outback['mpptStatus_str']
                last_solarPower = dataset.outback['solarPower']
                last_policy = 'solar_fluctuate'
                loop_log = loop_log + ' 2' + ' solar_fluctuate(2)'
                print '>>>>>>>>>>>>>>>>>>>>>Just enter 2:solar_fluctuate'
            else:
                max_green.max_green(dataset, sys_log, ipdu_switch_count, filter_buffer, statset)
                statset.add_policy('max_green')
                last_mpptStatus = dataset.outback['mpptStatus_str']
                last_solarPower = dataset.outback['solarPower']
                last_policy = 'max_green'
                loop_log = loop_log + ' 1' + ' max_green(1)' 
                print '>>>>>>>>>>>>>>>>>>>>>Just enter 1:max_green'
        elif ((last_policy == 'solar_fluctuate') or (last_policy == 'solar_fluctuate_utility')):
            if dataset.outback['batteryVoltage_average'] >= globalValue.battery_voltage_up():
                max_green.max_green(dataset, sys_log, ipdu_switch_count, filter_buffer, statset)
                statset.add_policy('max_green')
                last_mpptStatus = dataset.outback['mpptStatus_str']
                last_solarPower = dataset.outback['solarPower']
                last_policy = 'max_green'
                loop_log = loop_log + ' 1' + ' max_green(3)' 
                print '>>>>>>>>>>>>>>>>>>>>>Just enter 3:max_green'
            elif dataset.outback['batteryVoltage_average'] < globalValue.battery_voltage_up():
                if last_policy == 'solar_fluctuate_utility':
                    solar_fluctuate.solar_fluctuate_utility(dataset, sys_log, ipdu_switch_count, statset)
                    statset.add_policy('solar_fluctuate')
                    last_mpptStatus = dataset.outback['mpptStatus_str']
                    last_solarPower = dataset.outback['solarPower']
                    last_policy = 'solar_fluctuate_utility'
                    loop_log = loop_log + ' 2' + ' solar_fluctuate_utility(4)' 
                    print '>>>>>>>>>>>>>>>>>>>Just enter 4:solar_fluctuate_utility'
                elif dataset.outback['batteryVoltage_average'] < globalValue.battery_voltage_down():
                    solar_fluctuate.solar_fluctuate_utility(dataset, sys_log, ipdu_switch_count, statset)
                    statset.add_policy('solar_fluctuate')
                    last_mpptStatus = dataset.outback['mpptStatus_str']
                    last_solarPower = dataset.outback['solarPower']
                    last_policy = 'solar_fluctuate_utility'
                    loop_log = loop_log + ' 2' + ' solar_fluctuate_utility(5)' 
                    print '>>>>>>>>>>>>>>>>>>>Just enter 5:solar_fluctuate_utility'
                elif idle_count[0] >= 10:    #if solar_fluctuate on server for 10 times
                    max_green.max_green(dataset, sys_log, ipdu_switch_count, filter_buffer, statset)
                    statset.add_policy('max_green')
                    last_mpptStatus = dataset.outback['mpptStatus_str']
                    last_solarPower = dataset.outback['solarPower']
                    last_policy = 'max_green'
                    loop_log = loop_log + ' 1' + ' max_green(6)' 
                    print '>>>>>>>>>>>>>>>>>>>Just enter 6:max_green'
                else:
                    solar_fluctuate.solar_fluctuate(dataset, sys_log, ipdu_switch_count, idle_count, statset)
                    statset.add_policy('solar_fluctuate')
                    last_mpptStatus = dataset.outback['mpptStatus_str']
                    last_solarPower = dataset.outback['solarPower']
                    last_policy = 'solar_fluctuate' 
                    loop_log = loop_log + ' 2' + ' solar_fluctuate(7)' 
                    print '>>>>>>>>>>>>>>>>>>>Just enter 7:solar_fluctuate'
        loop_log = loop_log + '\n'
        policy_log_fd = open(policy_log, 'a')
        policy_log_fd.write(loop_log)
        policy_log_fd.close()
        # for hmi
        hmi_monitor.hmi_monitor(dataset, statset)
     
        signal.pause()
        #prepare for the next loop
        try:
            cfg_fd = open(globalValue.policy_cfg_name(), 'r')
            i = cfg_fd.readlines(1)
            cfg_fd.close()
        except:
            pass    # keep using previous policy_name
        else:
            policy_name = i[0].strip('\n')
        if (policy_name in globalValue.policy_list()):
            loop_token = True
        else:
            loop_token = False

   


    #formal policy selector, according to policy.cfg file   
    '''
    while(loop_token):
        if (policy_name == 'solar_fluctuate'):
            solar_fluctuate.solar_fluctuate(sys_log)
        elif (policy_name == 'max_green'):
            print 'enter max_green'
            max_green.max_green(sys_log, ipdu_switch_count, filter_buffer)
        signal.pause()
        #prepare for the next loop
        try:
            cfg_fd = open(globalValue.policy_cfg_name(), 'r')
            i = cfg_fd.readlines(1)
            cfg_fd.close()
        except:
            pass    # keep using previous policy_name
        else:
            policy_name = i[0].strip('\n')
        if (policy_name in globalValue.policy_list()):
            loop_token = True
        else:
            loop_token = False
    '''
       
        

if __name__ == '__main__':
    main_loop()
