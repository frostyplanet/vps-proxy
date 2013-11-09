#!/usr/bin/env python
# coding:utf-8

import _env
from lib.log import Log
from lib.rpc import AES_RPC_Client, RPC_Exception
import traceback
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

    
    def __init__ (self, logger):
        self.logger = logger
        self.rpc = AES_RPC_Client(_private.KEY, logger)

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
            print traceback.print_exc()
            return
        conf = []
        for i in domain_list():
            conf.append(self.NGINX_TEMPLATE % {'host':i[2], 'ip':i[3], 'suffix': _private.PROXY_DOMAIN_SUFFIX})
        print conf


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
