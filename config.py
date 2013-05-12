#!/usr/bin/env python
# coding:utf-8

import os

base_dir = os.path.dirname (__file__)
# for log.py
log_dir = os.path.join (base_dir, "log")
log_rotate_size = 20000
log_backup_count = 3
log_level = "DEBUG" 

#end for log.py
RUN_DIR = os.path.join (base_dir, "run")

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
