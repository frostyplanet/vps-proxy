#!/usr/bin/env python
# coding:utf-8

import _env
from lib.log import Log
from lib.rpc import AES_RPC_Client, RPC_Exception
import hashlib
import traceback
import _private
import subprocess
import os
import config
assert config.NGINX_CONF_PATH
assert config.NGINX_RELOAD_CMD

def _md5(text):
    h = hashlib.md5()
    h.update(text)
    return h.hexdigest()

def _md5_file(filepath):
    f = open(filepath, "r")
    try:
        h = hashlib.md5()
        for l in f:
            h.update(l)
    finally:
        f.close()
    return h.hexdigest()


class VpsProxy(object):

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

    
    def __init__(self):
        self.logger = Log("proxy", config=config)
        self.logger_rpc = Log("proxy_rpc", config=config)
        self.output_path = config.NGINX_CONF_PATH
        self.nginx_reload_cmd = config.NGINX_RELOAD_CMD
        self.rpc = AES_RPC_Client(_private.KEY, self.logger_rpc)

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def loop(self):
        while self.is_running:
            self.gen_config()
            time.sleep(conf.RUN_INV)

    def reload_nginx(self):
        subprocess.check_output(self.nginx_reload_cmd)
        self.logger.info("nginx reloaded")
        print "nginx reloaded"

    def gen_config(self, force=False):
        domain_list = None
        try:
            self.rpc.connect(_private.SAAS_ADDR)
            try:
                domain_list = self.rpc.call("proxy_domain_list")
            finally:
                self.rpc.close()
        except Exception, e:
            self.logger.exception(e)
            print traceback.print_exc()
            return
        conf = []
        for i in domain_list:
            conf.append(self.NGINX_TEMPLATE % {'host':i["domain"], 'ip':i["ip"], 'suffix': _private.PROXY_DOMAIN_SUFFIX})
        content = "".join(conf)
        try:
            if not force and os.path.exists(self.output_path) and _md5_file(self.output_path) == _md5(content):
                print "skip the same"
                return
            f = open(self.output_path, "w")
            try:
                f.write(content)
            finally:
                f.close()
            self.logger.info("conf generated")
            self.reload_nginx()
        except Exception, e:
            self.logger.exception(e)
            print traceback.print_exc()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
