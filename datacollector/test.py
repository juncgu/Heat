import os, copy
import time
arr_1 = [0 for i in range(15)]
arr_2 = [0 for i in range(15)]
arr_3 = [0 for i in range(15)]
arr_4 = [0 for i in range(15)]
cmd = './datafilter 15'

for i in arr_1:
    cmd = cmd +' '+str(i)
for i in arr_2:
    cmd = cmd +' '+str(i)
for i in arr_3:
    cmd = cmd +' '+str(i)
fd = open('result.txt', 'a')

for i in open('test.txt', 'r'):
    tmp_cmd = copy.copy(cmd)
    if i != '\n':
        tmp = int(i.strip('\n'))
        for j in range(14, 0, -1):
            arr_4[j] = arr_4[j-1]
        arr_4[0] = tmp
        for k in arr_4:
            tmp_cmd = tmp_cmd +' '+str(k)
        tmp_cmd = tmp_cmd +' '+'0'
        buf = os.popen(tmp_cmd)
        re = eval(buf.read())
        fd.write(str(re['predict_workload'])+'\n')

fd.close()
