# -*- coding: utf-8 -*-
#
# Author: Mouchel Thomas <thomspirit@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import threading
import time
import sys
import os

from oslo.config      import cfg
from ceilometerclient import client as ceilometer_client
from execo            import Host, Remote, Put, logger
import keystoneclient.middleware.auth_token as auth_token
import keystoneclient.v2_0                  as keystone_client

from kwranking.api.benchmark import Benchmark
from kwranking.api.database  import SqlDatabase

app_opts = [
    cfg.IntOpt('refresh_interval',
               required=True,
               ),
]
cfg.CONF.register_opts(app_opts)

class Info(dict):
    """Contains fields (Wmin, Wmax, Flop) """

    def __init__(self, wmin, wmax, flop = -1, Efficiency = False, Timestamp = False):
        """Initializes fields with the given arguments."""
        dict.__init__(self)
        self._dict          = {}
        self['Wmin']        = wmin
        self['Wmax']        = wmax
        self['Flop']        = flop

        if(not Efficiency):
            self['Efficiency'] = flop / wmax
        else:
            self['Efficiency'] = Efficiency
        if(not Timestamp):
            self['Timestamp']  = int(round(time.time()))
        else:
            self['Timestamp']  = Timestamp

    def update(self, wmin, wmax, flop):
        """Update field with the given arguments."""
        self['Wmin']            = wmin
        self['Wmax']            = wmax
        if(flop != -1) :
            self['Flop']        = flop
        self['Efficiency']      = flop / wmax
        self['Timestamp']       = int(round(time.time()))

    def set(self, index, value):
        self[index]         = value
        self['Efficiency']  = self['Flop'] / self['Wmax']

class Storage(dict):
    """Storage gradually fills its database with received values from Ceilometer and Climate API"""

    def __init__(self):
        """Initializes an empty database."""
        self._dict       = {}
        self['lock']     = threading.Lock()
        self['list']     = {}
        self['sorted']   = {}
        self['wait']     = []
        self['sql']      = SqlDatabase()
        self['database'] = self['sql'].host_load()

    def wait(self, host):
        """Add host to waiting list"""
        self['wait'].append(host)

    def add(self, host, wmin, wmax, flop = -1):
        """Creates (or updates) ranking data for this host."""
        if host in self['database'].keys():
            self['database'][host].update(wmin, wmax, flop)
        else:
            record = Info(wmin, wmax, flop)
            self['database'][host] = record
        for method in self['sorted']:
            self['sorted'][method] = False

    def set(self, host, index, value):
        """Creates (or updates) ranking data for this host."""
        if host in self['database'].keys():
            self['database'][host].set(index, value)
            method_list = [index]
            if(index == "Flop" or index == "Wmax"): 
                method_list.append("Efficiency") 
            for method in method_list:
                self['sorted'][method] = False
            return self['database'][host]

    def remove(self, host):
        """Removes this host from database."""
        try:
            del self['database'][host]
            return True
        except KeyError:
            return False

    def isSorted(self, method):
        """Return if list <method> is sorted"""
        return (method in self['sorted'] and self['sorted'][method])

    def sort(self, method):
        """Sort database by <method>."""
        try:
            sorted_list = sorted(self['database'], key=lambda x: self['database'][x][method], 
                                                reverse= True if(method == "Flop" or method == "Efficiency") else False)
        except Exception, e:
            return False

        self['list'][method]   = sorted_list
        self['sorted'][method] = True
        return True

    def refresh(self):
        def consumption(host_id):
            """Host consumption will be collected"""
            host = host_id.split(':')
            info = ceilo.statistics.list('power', q=[{ 'field':'resource', 'op':'eq', 'value':host[0] }])
            if(len(info) >= 1):
                wmax = info[0].max
                wmin = info[0].min
                self.add(host_id, wmin, wmax)
                to_save[host_id] = self['database'][host_id]
                return True
            return False

        def benchmark_result(host_id, value):
            """Benchmark return value from host"""
            print("Benchmark result for " + host_id + " : " + str(value))
            host = {}
            host[host_id] = self.set(host_id, 'Flop', value)
            self['sql'].host_save(host)

        # List of hosts to save and remove
        to_save     = {}
        remove_list = []

        # Keystone identification
        ks = keystone_client.Client(username=   cfg.CONF.keystone_authtoken['admin_user'],
                                    password=   cfg.CONF.keystone_authtoken['admin_password'],
                                    tenant_name=cfg.CONF.keystone_authtoken['admin_tenant_name'],
                                    auth_url=   cfg.CONF.keystone_authtoken['auth_uri'])
        endpoint = ks.service_catalog.url_for(service_type='metering', endpoint_type='publicURL')
        ceilo    = ceilometer_client.Client('2', endpoint, token=(lambda: ks.auth_token))

        # Database Update
        for host_id in self['database']:
            host = self['database'][host_id]
            if( int(round(time.time() - host['Timestamp'])) >= cfg.CONF.refresh_interval):
                consumption(host_id)

        # Waiting list
        if(len(self['wait']) > 0):
            for host_id in self['wait']:
                if(consumption(host_id)):
                    remove_list.append(host_id)
            bench = Benchmark(remove_list, benchmark_result)
            bench.start()

        # Remove and Save
        self['wait'] = list(set(self['wait']) - set(remove_list))
        self['sql'].host_save(to_save)

        # Schedule periodic execution of this function
        if cfg.CONF.refresh_interval > 0:
            timer = threading.Timer(cfg.CONF.refresh_interval, self.refresh)
            timer.daemon = True
            timer.start()