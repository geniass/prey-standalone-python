# -*- coding: utf8 -*-

from flask import Flask, render_template, redirect, url_for, g, request
import sys
import requests
import elementtree.ElementTree as ET
from elementtree.ElementTree import XML, fromstring, tostring
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
        root = ET.Element("device")

        status = ET.SubElement(root, "status")
        missing = ET.SubElement(status, "missing")
        missing.text = "true"   # SET TO TRUE AT SOME POINT
        device_type = ET.SubElement(status, "device_type")
        device_type.text = "phone"

        config = ET.SubElement(root, "configuration")
        curr_release = ET.SubElement(config, "current_release")
        curr_release.text = "0.5.3"
        delay = ET.SubElement(config, "delay")
        delay.text = "20"
        post_url = ET.SubElement(config, "post_url")
        post_url.text = "https://prey-geniass.dotcloud.com/devices/" + device_id + "/reports.xml"
        auto_update = ET.SubElement(config, "auto_update")
        auto_update.text = "false"

        modules = ET.SubElement(root, "modules")
        system_module = ET.SubElement(modules, "module",
                attrib={"type": "action", "active": "true",
                    "name": "system", "version": "1.5"})
        network_module = ET.SubElement(modules, "module",
                attrib={"type":"report", "active": "true",
                    "name": "network", "version": "1.5"})
        geo_module = ET.SubElement(modules, "module",
                attrib={"type":"report", "active": "true",
                    "name": "geo", "version": "1.5"})

        print_stderr(tostring(root))
        return tostring(root)

    elif request.method == 'POST':
        pairs = request.data.split("&")
        keyvalue = {f[0]: f[1] for f in [x.split("=") for x in pairs]}

        print_stderr("Post Data (devices/[id].xml):" + str(keyvalue))

        if 'device%5Bnotification_id%5D' in keyvalue:
            global regId
            regId = keyvalue['device%5Bnotification_id%5D']
            print_stderr("REG: " + str(keyvalue['device%5Bnotification_id%5D']))
        elif 'device%5Bmissing%5D' in keyvalue:
            print_stderr("Device missing changed to: " + keyvalue['device%5Bmissing%5D'])

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
    print_stderr("Reg ID: " + str(regId))
    headers = {"content-type": "application/json",
                    "Authorization": "key=" + str(API_KEY)}
    payload = {"registration_ids": [regId], 
            "data": {"data": {"event":"message",
                    "data":{"type":"text","body":"run_once","key":device_id}}}}

    r = requests.post(GCM_URL, json.dumps(payload), headers=headers)

    return "<div>" + r.text + "</div>"


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


def print_stderr(message):
    print >> sys.stderr, message


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
