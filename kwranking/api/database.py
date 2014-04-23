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

#CREATE TABLE hosts( Id INT NOT NULL AUTO_INCREMENT, Ip VARCHAR(23) NOT NULL, Wmin VARCHAR(20) NOT NULL, Wmax VARCHAR(20) NOT NULL, Flop VARCHAR(20) NOT NULL, Efficiency VARCHAR(20) NOT NULL, Timestamp VARCHAR(20) NOT NULL, PRIMARY KEY ( Id ) );

from sqlalchemy                 import create_engine
from sqlalchemy.orm             import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, Integer, String
from oslo.config                import cfg

app_opts = [
    cfg.StrOpt('sql_type',
               required=True,
               ),
    cfg.StrOpt('sql_server',
               required=True,
               ),
    cfg.StrOpt('sql_port',
               required=True,
               ),
    cfg.StrOpt('sql_user',
               required=True,
               ),
    cfg.StrOpt('sql_password',
               required=True,
               ),
    cfg.StrOpt('sql_database',
               required=True,
               ),
    cfg.StrOpt('sql_uri',
               required=False,
               )
]
cfg.CONF.register_opts(app_opts)

Base = declarative_base()
class HostTable(Base):
	"""Create Table for SqlDatabase"""

	__tablename__ = 'hosts'
	Ip     		= Column(String(23), primary_key=True)
	Wmin 		= Column(String(20))
	Wmax 		= Column(String(20))
	Flop 		= Column(String(20))
	Efficiency 	= Column(String(20))
	Timestamp 	= Column(String(10))

	def __init__(self, ip, wmin, wmax, flop, efficiency, timestamp):
	        self.Ip 		= ip
	        self.Wmin 		= wmin
	        self.Wmax 		= wmax
	        self.Flop 		= flop
	        self.Efficiency = efficiency
	        self.Timestamp 	= timestamp

	def __repr__(self):
	        return "<HostTable(%s, %s, %s, %s, %s, %s)>" % (self.Ip, self.Wmin, self.Wmax, self.Flop, self.Efficiency, self.Timestamp)

class SqlDatabase:
	"""Create MySql database access"""

	def __init__(self):
		self.session = None
		if(cfg.CONF.sql_uri != None):
			self.uri = cfg.CONF.sql_uri
		else:
			self.uri = cfg.CONF.sql_type + "://" + cfg.CONF.sql_user + ":" + cfg.CONF.sql_password + "@" + cfg.CONF.sql_server + ":" + cfg.CONF.sql_port + "/" + cfg.CONF.sql_database

	def _connect(self):
		"""Create connection and table if not exist"""
		engine       = create_engine(self.uri, echo=False)
		Session      = sessionmaker(bind=engine)
		self.session = Session()
		Base.metadata.create_all(engine)

	def host_save(self, hosts_list):
		"""Save or Update hosts from Database"""
		self._connect()

		records_list = []
		for ip in hosts_list:
			host = hosts_list[ip]
			self.session.merge(HostTable(ip, host['Wmin'], host['Wmax'], host['Flop'], host['Efficiency'], host['Timestamp']))
		self.session.commit()

	def host_load(self):
		"""Return list of hosts from Database"""
		from kwranking.api.storage import Info

		self._connect()

		records_list = self.session.query(HostTable).all()
		hosts_list 	 = {}
		for record in records_list:
			hosts_list[record.Ip] = Info(record.Wmin, float(record.Wmax), float(record.Flop), float(record.Efficiency), int(record.Timestamp))

		return hosts_list