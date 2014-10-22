#datacollector
#use hmi

import sys
import os
import data_collect, filterBuffer

def hmi_data_filter(dataset, filter_buffer):
    ABS_path = os.path.split(os.path.realpath(__file__))[0]
    cmd = ABS_path + "/datafilter "

    cmd = cmd + str(filter_buffer.buf_len) + ' '

    for j in filter_buffer.buf_current1:
        cmd = cmd + str(j) + ' '
    for i in filter_buffer.buf_current2:
        cmd = cmd + str(i) + ' '
    for j in filter_buffer.buf_solar:
        cmd = cmd + str(j) + ' '
    for i in filter_buffer.buf_workload:
        cmd = cmd + str(i) + ' '
    cmd = cmd + str(filter_buffer.battery_current)

    print cmd
    
    output = os.popen(cmd)
    result = eval(output.read())
    print result
    return result


if __name__ == '__main__':
    dataset = data_collect.DataCollection()
    filterbuffer = filterBuffer.filterBuffer()
    hmi_data_filter(dataset, filterbuffer)
