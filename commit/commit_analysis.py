import cpufreq_dvfs, ipdu_switch, vm_migration, hmi_relay, path
import time
import sys, os

#analysis the commit_cmd from policy module
#normally, this should be called by policy
def commit_analysis_execute(commit_dict):
    print "Enter Commit..."
    #Step1:  ipdu switch
    #   1.1: open port
    if commit_dict == {}:
        print "NO actions to be taken..."
        return 0
    opcode = [0,0,0,0,0,0,0,0]
    if ((commit_dict.has_key('open_port')) and (len(commit_dict['open_port']) != 0)):
#        for i in commit_dict['open_port']:
#            opcode[i] = 2
        ipdu_open_analysis(commit_dict['open_port'])

        #   1.2: close port
    if ((commit_dict.has_key('close_port')) and (len(commit_dict['close_port']) != 0)):
#        for j in commit_dict['close_port']:
#            opcode[j] = 1
        ipdu_close_analysis(commit_dict['close_port'])

#    if ((commit_dict.has_key('open_port')) or (commit_dict.has_key('close_port'))):
#        if ((len(commit_dict['open_port']) != 0) or (len(commit_dict['close_port']) != 0)):
#            print "ipdu switch: ",opcode
#            ipdu_switch.ipdu_single_commit(opcode)

    #Step2: dvfs
    if ((commit_dict.has_key('revoke_dvfs')) and (len(commit_dict['revoke_dvfs']) != 0)):
        for (host, freq) in commit_dict['revoke_dvfs'].items():
            cpufreq_dvfs.cpufreq_dvfs_commit(host, freq)
            print "dvfs: ", host, freq
    
    #Step3: vm migration
    if ((commit_dict.has_key('vm_migration')) and (len(commit_dict['vm_migration']) != 0)):
        for k in commit_dict['vm_migration']:
            print "vm migration: ", k['vmid'], k['dest']
            vm_migration.vm_migration_commit(k['vmid'], k['dest'])

    #Step4: relay_ctl
    if ((commit_dict.has_key('relay_port')) and (len(commit_dict['relay_port']) != 0)):
        hmi_relay.hmi_relay_execute(commit_dict['relay_port']) 


def ipdu_open_analysis(oplist):
    if oplist == []:
        print "NO ipdu actions..."
        return 0
    opcode = [0,0,0,0,0,0,0,0]
    for i in oplist:
        opcode[i] = 2
    ipdu_switch.ipdu_single_commit(opcode)
    time.sleep(5)     

def ipdu_close_analysis(oplist):
    if oplist == []:
        print "NO ipdu actions..."
        return 0
    count = 0
    i = avoid_shutdown(oplist)
    while(i >= 0):
        print 'Shutdown Risk...'
        time.sleep(10) 
        count += 1
        if (count <= 2):
            i = avoid_shutdown(oplist)
        else:
            print 'Check the physical status of IPDU...'
            oplist.remove(i)
            i = avoid_shutdown(oplist)

    opcode = [0,0,0,0,0,0,0,0]
    for i in oplist:
        opcode[i] = 1
    ipdu_switch.ipdu_single_commit(opcode)


# ensure each server has at least one power supply
def avoid_shutdown(oplist):
    sys.path.append(path.upper_path())
    from datacollector import data_collect
    dataset = data_collect.DataCollection()
    dataset.get_ipdu_outback()
    
    for i in oplist:
        if dataset.ipdu['status'][(i+4)%8] == 1:    #get the corresponding ipdu port
            pass
        else:
            return i
    return -1


if __name__ == '__main__':
    print "Enter commit analysis"
