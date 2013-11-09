#!/usr/bin/env python
# coding:utf-8

from lib.log import Log
import threading
import signal
import time
import sys
import lib.daemon as daemon
import json
import config
import os
from mod.vps_proxy import VpsProxy



def main ():
    logger = Log(config=config)
    client = VpsProxy (logger)
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
    p = VpsProxy (Log(config=config))
    p.gen_config ()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
