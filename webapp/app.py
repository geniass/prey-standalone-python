# -*- coding: utf8 -*-

from flask import Flask, render_template, redirect, url_for, g, request
import sys
import requests
import json

app = Flask(__name__)
regId = None

GCM_URL = "https://android.googleapis.com/gcm/send"
API_KEY = "AIzaSyCGDI006zQ4V0I-GKYVakVkEBD8Gp0JfRI"

@app.route('/')
def homepage():
    print >> sys.stderr, "HOMEPAGE!"
    return render_template('homepage.html')


@app.route('/users.xml', methods=['POST'])
def users():
    if request.method == 'POST':
        #app.logger.debug(request.data)
        print >> sys.stderr, request.data
        #print_stderr(request.data)
        return "<key>34332</key>"


"""This stuff's all hardcoded for now"""
@app.route('/devices.xml', methods=['POST'])
def devices():
    if request.method == 'POST':
        pairs = request.data.split("&")
        keyvalue = {f[0]: f[1] for f in [x.split("=") for x in pairs]}

        print_stderr("Request Data (devices.xml):" + str(keyvalue))

        return """<?xml version="1.0" encoding="UTF-8"?>
                    <device><key>akf7ef</key></device>"""


@app.route('/devices/<device_id>.xml', methods=['GET', 'POST', 'PUT'])
def device(device_id):
    if request.method == 'GET':
        print_stderr("Get params (devices/[id].xml):" + str(request.args.items()))

    elif request.method == 'POST':
        pairs = request.data.split("&")
        keyvalue = {f[0]: f[1] for f in [x.split("=") for x in pairs]}

        print_stderr("Post Data (devices/[id].xml):" + str(keyvalue))

        global regId
        regId = keyvalue["device[notification_id]"]

    elif request.method == 'PUT':
        print_stderr("Put Data (devices/[id].xml):" + str(request.data))

    return "<data></data>"


@app.route('/devices/<device_id>/reports.xml')
def reports(device_id):
    if request.method == 'GET':
        print_stderr("Get params (devices/[id].xml):" + str(request.args.items()))
    elif request.method == 'POST':
        print_stderr("Post Data (devices/[id].xml):" + str(request.data))
    elif request.method == 'PUT':
        print_stderr("Put Data (devices/[id].xml):" + str(request.data))
    return "<data></data>"


@app.route('/devices/<device_id>/missing')
def missing(device_id):
    headers = {"content-type": "application/json",
                    "Authorization": "key=" + str(API_KEY)}
    payload = {"registration_ids": regId, 
                "data": {"event":"message",
                    "data":{"type":"text","body":"run_once","key":device_id}}}

    r = requests.post(GCM_URL, json.dumps(payload), headers=headers)


@app.route('/profile.xml', methods=['GET'])
def profile():
    if request.method == 'GET':
        #ADD HTTP BASIC AUTH
        print_stderr("Get Params (profile.xml): " + str(request.args.items()))
        return """<?xml version="1.0" encoding="UTF-8"?>
                    <user>
                    <id>1078832</id>
                    <key>kliyrhapg43v</key>
                    <available_slots>1</available_slots>
                    </user>"""


@app.route('/reports.xml', methods=['POST'])
def reports():
    if request.method == 'POST':
        #app.logger.debug(request.data)
        print_stderr(request.data)



def print_stderr(message):
    print >> sys.stderr, message


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
