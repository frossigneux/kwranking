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

"""This blueprint defines all URLs and answers."""

import flask
from operator  import attrgetter
from itertools import islice
import random

blueprint = flask.Blueprint('v1', __name__)

@blueprint.route('/')
def welcome():
    """Return detailed information about this specific version of the API."""
    return 'Welcome to Kwranking!'

@blueprint.route('/hosts/get-rank/', methods=["POST"])
def rank_hosts_list():
    """Return organized list by <method> with <number> elements"""
    """<method> can be : Flop, Wmin, Wmax, Efficiency"""
    if (flask.request.method != 'POST'):
        return flask.jsonify({"error": True, "message": "Bad request method, must be <POST>."})

    try:
        hosts       = flask.request.form["hosts"].split()
        method      = flask.request.form["method"]
        number      = int(flask.request.form["number"])
    except:
        return flask.jsonify({"error": True, "message": "Missing arguments <hosts>, <method>, <number>."})

    hosts_db    = {}
    hosts_alone = {}
    for host in hosts:
        if(host in flask.request.collector.database.keys()):
            hosts_db[host] = flask.request.collector.database[host]
        else:
            hosts_alone[host] = host
    try:
        hosts_final = sorted(hosts_db, key=lambda x: hosts_db[x][method], reverse= True if(method == "Flop" or method == "Efficiency") else False)[:number]
    except Exception, e:
        return flask.jsonify({"error": True, "message": "Unknow method: " + e.message})

    message = {}
    message['hosts'] = hosts_final
    return flask.jsonify(message)

@blueprint.route('/hosts/set/', methods=["POST"])
def add_hosts_list():
    """Put new Host to list"""
    if (flask.request.method == 'POST'):
        if("host" in flask.request.form):
            flask.request.collector.add(flask.request.form['host'], random.randint(1, 1000), random.randint(1, 1000), random.uniform(0, 5))
            return flask.jsonify({"error": False, "message": "Operation successful."})
        else:
            return flask.jsonify({"error": True, "message": "Missing argument <host>."})

@blueprint.route('/hosts/get/<host>/')
def get_hosts(host):
    """Return host informations"""
    message = {}
    try:
        message[host] = flask.request.collector.database[host]
    except KeyError:
        flask.abort(404)
    return flask.jsonify(hosts=message)

@blueprint.route('/hosts/get/')
def get_hosts_list():
    """Return list of hosts (detailed)"""
    message = {}
    for host in flask.request.collector.database.keys():
        message[host] = flask.request.collector.database[host]
    return flask.jsonify(hosts=message)

@blueprint.route('/hosts/get-id/')
def get_hosts_id_list():
    """Return list of hosts (id)"""
    return flask.jsonify(hosts=flask.request.collector.database.keys())
