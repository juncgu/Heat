#commit: cpufreq_dvfs.py
import paramiko
from sys import argv, exit
from timeit import Timer
import time

def cpufreq_dvfs_commit(host_ip, freq):
    ip = host_ip
    port = 22
    user = 'root'
    passwd = 'ideal123'
    set_g_0 = 'cpufreq-set -c 0 -g userspace'
    set_g_1 = 'cpufreq-set -c 1 -g userspace'
    set_g_2 = 'cpufreq-set -c 2 -g userspace'
    set_g_3 = 'cpufreq-set -c 3 -g userspace'
    set_g_4 = 'cpufreq-set -c 4 -g userspace'
    set_g_5 = 'cpufreq-set -c 5 -g userspace'
    set_g_6 = 'cpufreq-set -c 6 -g userspace'
    set_g_7 = 'cpufreq-set -c 7 -g userspace'
    set_f_0_n = 'cpufreq-set -c 0 -f '
    set_f_1_n = 'cpufreq-set -c 1 -f '
    set_f_2_n = 'cpufreq-set -c 2 -f '
    set_f_3_n = 'cpufreq-set -c 3 -f '
    set_f_4_n = 'cpufreq-set -c 4 -f '
    set_f_5_n = 'cpufreq-set -c 5 -f '
    set_f_6_n = 'cpufreq-set -c 6 -f '
    set_f_7_n = 'cpufreq-set -c 7 -f '
    retrieve_freq = 'cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq'
    t=paramiko.SSHClient()
    t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    t.connect(ip, port, user, passwd)
    try:
        stdin, stdout, stderr = t.exec_command(retrieve_freq)
    except:
        print ">>>DVFS error: can't retrieve CPU freq info"
        print "         maybe ", ip, " doesn't support DVFS!"
    max_freq = stdout.readlines()[0].strip('\n')
    print max_freq
    print freq
    time.sleep(10)
    set_f_0 = set_f_0_n + freq + 'KHz'
    set_f_1 = set_f_1_n + freq + 'KHz'
    set_f_2 = set_f_2_n + freq + 'KHz'
    set_f_3 = set_f_3_n + freq + 'KHz'
    set_f_4 = set_f_4_n + freq + 'KHz'
    set_f_5 = set_f_5_n + freq + 'KHz'
    set_f_6 = set_f_6_n + freq + 'KHz'
    set_f_7 = set_f_7_n + freq + 'KHz'
    try:
        stdin, stdout, stderr = t.exec_command(set_g_0)
        stdin, stdout, stderr = t.exec_command(set_g_1)
        stdin, stdout, stderr = t.exec_command(set_g_2)
        stdin, stdout, stderr = t.exec_command(set_g_3)
        stdin, stdout, stderr = t.exec_command(set_g_4)
        stdin, stdout, stderr = t.exec_command(set_g_5)
        stdin, stdout, stderr = t.exec_command(set_g_6)
        stdin, stdout, stderr = t.exec_command(set_g_7)

        stdin, stdout, stderr = t.exec_command(set_f_0)
        stdin, stdout, stderr = t.exec_command(set_f_1)
        stdin, stdout, stderr = t.exec_command(set_f_2)
        stdin, stdout, stderr = t.exec_command(set_f_3)
        stdin, stdout, stderr = t.exec_command(set_f_4)
        stdin, stdout, stderr = t.exec_command(set_f_5)
        stdin, stdout, stderr = t.exec_command(set_f_6)
        stdin, stdout, stderr = t.exec_command(set_f_7)
    except:
        print ">>>DVFS error: ", ip, " does't support DVFS!" 

    t.close()

if __name__ == "__main__":
    print "Starting modify to max frequency..."
    cpufreq_dvfs_commit('controller', "3000");
