..
      Copyright 2013 François Rossigneux (Inria)

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

=======================
Kwranking documentation
=======================

Kwranking provides information about host efficiency.
It deploys UnixBench on remote hosts using SSH and runs arithmetic tests.
The returned value is stored in the DB (it never changes over time).
During the tests, the max power consumption is reached and stored in Ceilometer,
so the flop/w metric is build using the max power value retrieved in Ceilometer and the flop value returned by the benchmark.
The flop/w metric is updated periodically, because the max power consumption may vary over the machine lifetime.
An API allows the user to find the most efficient hosts from a list of hosts passed as parameter.
Kwranking could be used to improve scheduling strategies.
This documentation offers information on how Kwranking works.

==========
Installing
==========

Installing Kwranking
====================

1. Clone the Kwranking git repository to the management server::

   $ git clone https://github.com/frossigneux/kwranking

2. As a user with ``root`` permissions or ``sudo`` privileges, run the
   Kwranking installer and copy the configuration files::

   $ pip install kwranking
   $ cp -r kwranking/etc/kwranking /etc/

Running Kwranking service
=========================

   Start the Kwranking API::

   $ kwranking-api

=====================
Configuration Options
=====================

The following table lists the Kwranking options in the configuration file.
Please note that Kwranking uses openstack-common extensively,
which requires that the other parameters are set appropriately.

===================  ==============================  =====================================================================
Parameter            Default                         Note
===================  ==============================  =====================================================================
api_port             5001                            API port
acl_enabled          true                            Keystone authentication
policy_file          /etc/kwranking/policy.json      Access rules
log_file             /var/log/kwranking.log          Log file
refresh_interval     5184000                         Interval between two requests to Ceilometer to retrieve the max value
sql_type             mysql                           SQL type
sql_server           localhost                       SQL server
sql_port             3306                            SQL port
sql_user             root                            SQL user
sql_password         password                        SQL password
sql_database         kwranking                       SQL database
===================  ==============================  =====================================================================

The config file contains also a section dedicated to Keystone authentication (credentials used to contact Ceilometer).

===================  ==============================  ============
Parameter            Default                         Note
===================  ==============================  ============
auth_uri             http://localhost:35357/v2.0     Auth URI
admin_user           ceilometer                      Admin
admin_password       password                        Password
admin_tenant_name    service                         Tenant name
===================  ==============================  ============

A sample configuration file can be found in `kwranking.conf`_.

.. _kwranking.conf: https://github.com/frossigneux/kwranking/blob/master/etc/kwranking/kwranking.conf

API
===

====  ========================  ==================================================================================================================================================  =========================================
Verb  URL	                    Parameters	                                                                                                                                        Expected result
====  ========================  ==================================================================================================================================================  =========================================
GET   /v1/hosts/get-id/                                                                                                                                                             Returns all hosts IDs
GET   /v1/hosts/get/                                                                                                                                                                Returns all hosts details
GET   /v1/hosts/get/<host>/     host                                                                                                                                                Returns the host details
POST  /v1/hosts/get-rank/       ``{ "hosts":  host list separated by ';', "method": ranking method (Efficiency or Flop or Wmax or Wmin), "number": number of hosts to return }``    Ranks the hosts passed as parameter
PUT   /v1/hosts/set/            ``{ "host": hostname }``                                                                                                                            Add a host to benchmark in the database
====  ========================  ==================================================================================================================================================  =========================================

=======================
Project Hosting Details
=======================

:Code Hosting: https://github.com/frossigneux/kwranking
