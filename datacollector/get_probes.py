import get_token, path
import pycurl, sys, copy, simplejson, cStringIO
from sys import argv
import os
#upper_path = os.getcwd()[0:-14]
sys.path.append(path.upper_path())
#sys.path.append('/root/solar/Heat')
from policy import globalValue
from policy import emergency

class data:
    def __init__(self):
        self.head = ''
        self.body = []
    def body_write(self, buf):
#        print buf
        re_dict = simplejson.loads(buf)
#        re_dict = eval(buf)
#        print re_dict
        self.body = copy.copy(re_dict)
    def head_write(self, buf):
        self.head = self.head + buf 

def get_probes():
    token = get_token.get_token() 
    head = ["Content-Type: application/json", "Accept: application/json"]
    header = "X-Auth-Token: " + token
    head.append(header)
#    url = 'http://controller:5001/v1/probes/'
    url = globalValue.data_probes_url()
    #d = data()
    body = cStringIO.StringIO()
    headd = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.HTTPHEADER, head)
#    c.setopt(c.HTTPHEADER, [header])
    c.setopt(c.CUSTOMREQUEST, "GET")
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(c.URL, url)
    c.setopt(c.HEADERFUNCTION, headd.write)
    c.setopt(c.WRITEFUNCTION, body.write)
    try:
        c.perform()
    except pycurl.error:
        print "Error: get_probes: c.perform()"
        emergency.turn_on_utility()
        
    c.close()
    re_dict = simplejson.loads(body.getvalue())
    pro = copy.copy(re_dict)
    print pro['probes']
    return pro['probes']

if __name__ == '__main__':
    print "GET probes"
    print get_probes()

