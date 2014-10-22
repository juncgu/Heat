import pycurl, sys, urllib, copy
import path
from sys import argv
import simplejson, cStringIO
import os
#upper_path = os.getcwd()[0:-14]
sys.path.append(path.upper_path())
from policy import emergency
class data:
    def __init__(self):
        self.head = ''
        self.body = []
    def body_write(self, buf):
        re_dict = simplejson.loads(buf)
        self.body = copy.copy(re_dict)
    def head_write(self, buf):
        self.head = self.head + buf
def get_token(): 
    head = ["Content-Type: application/json", "Accept: application/json", "User-Agent: python-novaclient"]
    postfield = '{"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "ADMIN_PASS"}}}' 
    url = 'http://10.227.56.232:35357/v2.0/tokens'
    header = cStringIO.StringIO()
    body = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.CUSTOMREQUEST, 'POST')
    c.setopt(c.HTTPHEADER, head)
    c.setopt(c.POSTFIELDS, postfield)
    c.setopt(c.HEADER, 0)
    c.setopt(c.USERAGENT, "curl/7.22.0 (x86_64-pc-linux-gnu) libcurl/7.22.0 OpenSSL/1.0.1 zlib/1.2.3.4 libidn/1.23 librtmp/2.3")
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(c.URL, url)
    c.setopt(c.HEADERFUNCTION, header.write)
    c.setopt(c.WRITEFUNCTION, body.write)
    try:
        c.perform()
    except:
        print "Error: get_token: c.perform()"
        emergency.turn_on_utility()

    c.close()
    re_dict = simplejson.loads(body.getvalue())
    token_id = copy.copy(re_dict)
    return token_id['access']['token']['id']

if __name__ == '__main__':
    print get_token()
