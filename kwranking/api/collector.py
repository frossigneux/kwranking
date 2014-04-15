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

class Record(dict):
    """Contains fields (Wmin, Wmax, Flop) """

    def __init__(self, wmin, wmax, flop):
        """Initializes fields with the given arguments."""
        dict.__init__(self)
        self._dict          = {}
        self['Wmin']        = wmin
        self['Wmax']        = wmax
        self['Flop']        = flop
        self['Efficiency']  = flop / wmax

    def update(self, wmin, wmax, flop):
        """Update field with the given arguments."""
        self['Wmin']        = wmin
        self['Wmax']        = wmax
        self['Flop']        = flop
        self['Efficiency']  = flop / wmax

class Collector:
    """Collector gradually fills its database with received values from
    Cilometer and Climate API

    """

    def __init__(self):
        """Initializes an empty database and start listening the endpoint."""
        self.database = {}
        self.lock = threading.Lock()

    def add(self, host, wmin, wmax, flop):
        """Creates (or updates) ranking data for this host."""
        if host in self.database.keys():
            self.database[host].update(wmin, wmax, flop)
        else:
            record = Record(wmin, wmax, flop)
            self.database[host] = record

    def remove(self, host):
        """Removes this host from database."""
        try:
            del self.database[host]
            return True
        except KeyError:
            return False
