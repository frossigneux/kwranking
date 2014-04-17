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
        hosts       = flask.request.form["hosts"].split() if(flask.request.form["hosts"] != "*") else flask.request.storage['database'].keys()
        method      = flask.request.form["method"]
        number      = int(flask.request.form["number"])
    except:
        return flask.jsonify({"error": True, "message": "Missing arguments <hosts>, <method>, <number>."})

    if(flask.request.storage.isSorted(method) != True):
        flask.request.storage.sort(method)

    try:
        hosts_db    = flask.request.storage['list'][method]
    except:
        return flask.jsonify({"error": True, "message": "Unknow <method>."})

    hosts_final = filter(lambda x: x in hosts, hosts_db)
    hosts_alone = list(set(hosts_db) - set(hosts_final))

    message = {}
    message['hosts'] = (hosts_final + hosts_alone)[:number]
    return flask.jsonify(message)

@blueprint.route('/hosts/set/', methods=["POST"])
def add_hosts_list():
    """Put new Host to list"""
    if (flask.request.method == 'POST'):
        if("host" in flask.request.form and len(flask.request.form['host']) >= 1):
            flask.request.storage.add(flask.request.form['host'], random.randint(1, 500), random.randint(500, 1000), random.uniform(0, 5))
            return flask.jsonify({"error": False, "message": "Operation successful."})
        else:
            return flask.jsonify({"error": True, "message": "Missing argument <host>."})

@blueprint.route('/hosts/wait/', methods=["POST"])
def add_waiting_list():
    """Put new Host to list"""
    if (flask.request.method == 'POST'):
        if("host" in flask.request.form):
            flask.request.storage.wait(flask.request.form['host'])
            return flask.jsonify({"error": False, "message": "Operation successful."})
        else:
            return flask.jsonify({"error": True, "message": "Missing argument <host>."})

@blueprint.route('/hosts/get/<host>/')
def get_hosts(host):
    """Return host informations"""
    message = {}
    try:
        message[host] = flask.request.storage['database'][host]
    except KeyError:
        flask.abort(404)
    return flask.jsonify(hosts=message)

@blueprint.route('/hosts/get/')
def get_hosts_list():
    """Return list of hosts (detailed)"""
    message = {}
    for host in flask.request.storage['database'].keys():
        message[host] = flask.request.storage['database'][host]
    return flask.jsonify(hosts=message)

@blueprint.route('/hosts/get-id/')
def get_hosts_id_list():
    """Return list of hosts (id)"""
    return flask.jsonify(hosts=flask.request.storage['database'].keys())

