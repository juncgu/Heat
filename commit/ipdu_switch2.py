#commit: ipdu_switch.py
#uses ipdu_switch.sh

import os
import sys

def ipdu_switch_commit(opcode):
    ABS_path = os.path.split(os.path.realpath(__file__))[0]    
    ON_cmd = ABS_path + "/ipdu_switch.sh "
    OFF_cmd = ABS_path + "/ipdu_switch.sh "

    for i in range(8):
        if opcode[i] == 2:
            ON_cmd += "5 "
        else:
            ON_cmd += "0 "
    print "The first ON cmd :", ON_cmd
 
    if os.system(ON_cmd) == 1:
        print "ON cmd execute success"    

    for i in range(8):
        if opcode[i] == 1:
            OFF_cmd += "6 "
        else:
            OFF_cmd += "0 "
    print "The second OFF cmd :", OFF_cmd
    
    if os.system(OFF_cmd) == 1:
        print "OFF cmd execute success"

def ipdu_single_commit(opcode):
    ABS_path = os.path.split(os.path.realpath(__file__))[0]
    cmd  = ABS_path + "/ipdu_single.sh "
    if opcode == []:
        return 0
    for i in range(8):
        if opcode[i] == 1:
            cmd += (str(i+1) + ' 6')
            print cmd
#            if os.system(cmd) == 1:
#                print "ipdu single cmd execute success"
        elif opcode[i] == 2:
            cmd += (str(i+1) + ' 5')
            print cmd
#            if os.system(cmd) == 1:
#                print "ipdu single cmd execute success"       

if __name__ == '__main__':
#    print len([1,2,0,2,1,0,1,2])
#    print [1,2,0,2,0,1,1,2]
#    ipdu_switch_commit([1,1,1,1,2,2,2,2])
    ipdu_single_commit([0,0,0,0,1,0,0,0])
