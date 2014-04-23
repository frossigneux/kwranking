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

import os, sys

from execo import Host, Remote, Put, logger, ProcessOutputHandler

class Benchmark:
    """Run Benchmark on remote hosts."""

    def __init__(self, hosts_list, callback):
			self.bench_list = {}
			self.callback   = callback
			for host_id in hosts_list:
				host = host_id.split(':')
				if(len(host) < 2): host.append(False)
				self.bench_list[host_id] = Host(host[0], port=int(host[1]))

    def start(self):
		logger.info('Put benchmarking files on hosts.')
		file_path  = os.path.join(os.path.dirname(__file__), '../resources/unixbench-5.1.3.tgz')
		bench_copy = Put(self.bench_list.values(), [file_path], "/tmp/").run()

		logger.info('Start benchmarking on ' + str(len(self.bench_list)) + ' hosts.')
		bench_install = Remote( 'cd /tmp/ &&'                     + \
								'tar xvfz unixbench-5.1.3.tgz &&' + \
								'cd unixbench-5.1.3/ &&'          + \
								'./Run arithmetic &&'             + \
								'cd ../ &&'                       + \
								'rm -rf unixbench-5.1.3/ &&'      + \
								'rm -rf unixbench-5.1.3.tgz',
								self.bench_list.values())

		for p in bench_install.processes:
			host = p.host.address + (':' + str(p.host.port)) if(p.host.port != None) else ""
			p.stdout_handlers.append(end_forwarder_stdout_handler(host, self.callback))

		bench_install.start()

class end_forwarder_stdout_handler(ProcessOutputHandler):
    """parses verbose ssh output to save when benchmarking is finish"""

    def __init__(self, host, callback):
        super(end_forwarder_stdout_handler, self).__init__()
        self.search   = "System Benchmarks Index Score (Partial Only)"
        self.host     = host
        self.callback = callback

    def read_line(self, process, string, eof, error):
        if self.search in string:
			self.callback(self.host, float(self._parse_output(string)))

    def _parse_output(self, stdout):
		return stdout.split()[-1]