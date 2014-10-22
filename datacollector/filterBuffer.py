#datacollector: filterButter
#    buffer the interval data in the list
class filterBuffer:
    buf_current1 = []
    buf_current2 = []
    buf_solar = []
    buf_workload = []
    battery_current = 0.0
    buf_len = 0

    def __init__(self, num=15):
        self.buf_len = num
        self.buf_current1 = [0 for i in range(num)]
        self.buf_current2 = [0 for i in range(num)]
        self.buf_solar = [0 for i in range(num)]
        self.buf_workload = [0 for i in range(num)]

#    def __init__(self):
#        self.buf_len = 15
#        self.buf_current1 = [0 for i in range(15)]
#        self.buf_current2 = [0 for i in range(15)]
#        self.buf_solar = [0 for i in range(15)]
#        self.buf_workload = [0 for i in range(15)]


    def insert(self, current1, current2, solar, workload, batt_cur):
        for i in range(self.buf_len-1, 0, -1):
            self.buf_current1[i] = self.buf_current1[i-1]
            self.buf_current2[i] = self.buf_current2[i-1]
            self.buf_solar[i] = self.buf_solar[i-1]
            self.buf_workload[i] = self.buf_workload[i-1]
        self.buf_current1[0] = current1
        self.buf_current2[0] = current2
        self.buf_solar[0] = solar
        self.buf_workload[0] = workload
        self.battery_current  = batt_cur


