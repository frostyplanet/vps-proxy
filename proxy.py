#!/usr/bin/env python
# coding:utf-8

from lib.log import Log
import threading
import signal
import time
import sys
import lib.daemon as daemon
from lib.rpc import SSL_RPC_Client, RPC_Exception
import json
import config
import os
import _private


class VpsProxy (object):

    NGINX_TEMPLATE = """
server {
    listen      80;
    server_name %(host)s *.%(host)s;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header REMOTE-HOST $remote_addr;
    proxy_set_header HOST $host.%(suffix)s;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    location / {
        proxy_pass http://%(ip)s;
    }
}
"""

    
    def __init__ (self):
        self.logger = Log ("proxy", config=config)
        self.rpc = SSL_RPC_Client (self.logger)

    def start (self):
        self.is_running = True

    def stop (self):
        self.is_running = False

    def loop (self):
        while self.is_running:
            self.gen_config ()

    def gen_config (self):
        domain_list = None
        try:
            self.rpc.connect (_private.SAAS_ADDR)
            try:
                domain_list = self.rpc.call ("domain_list")
            finally:
                self.rpc.close ()
        except Exception, e:
            self.logger.exception (e)
            print str(e)
            return
        conf = []
        for i in domain_list():
            conf.append(self.NGINX_TEMPLATE % {'host':i[2], 'ip':i[3], 'suffix': _private.PROXY_DOMAIN_SUFFIX})
        print conf

        


def main ():
    client = VpsProxy ()
    def exit_sig_handler (sig_num, frm):
        global stop_signal_flag
        if stop_signal_flag:
            return
        stop_signal_flag = True
        client.stop ()
        return
    client.start ()
    signal.signal (signal.SIGTERM, exit_sig_handler)
    signal.signal (signal.SIGINT, exit_sig_handler)
    client.loop ()
    return

def usage ():
    print "usage:\t%s star/stop/restart\t#manage forked daemon" % (sys.argv[0])
    print "\t%s run\t\t# run without daemon, for test purpose" % (sys.argv[0])
    os._exit (1)

if __name__ == '__main__':
#    if len (sys.argv) <= 1:
#        usage ()
#    else:
#        logger = Log ("daemon", config=config) # to ensure log is permitted to write
#        pid_file = "mtgox_streamproc.pid"
#        mon_pid_file = "mtgox_streamproc_mon.pid"
#        action = sys.argv[1]
#        daemon.cmd_wrapper (action, main, usage, logger, config.log_dir, config.RUN_DIR, pid_file, mon_pid_file)
    p = VpsProxy ()
    p.gen_config ()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
