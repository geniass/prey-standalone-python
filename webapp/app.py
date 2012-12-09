# -*- coding: utf8 -*-

from flask import Flask, render_template, redirect, url_for, g, request
import sys
import requests
import elementtree.ElementTree as ET
from elementtree.ElementTree import XML, fromstring, tostring
import json
import pymongo
import hashlib, uuid

app = Flask(__name__)
regId = "APA91bGOKc5MucM4tXVENh7bbUSCveszrctTIfhjFFGNz08NSWCpBhkL2e8LfRU3MhNRuQNdFcNYMiDnXfLPmgBXAgG9NYbDB9IYaFrau0tCvkAbSql6VrSLeaTYWze_wiVMHJUk1JRH"

GCM_URL = "https://android.googleapis.com/gcm/send"
API_KEY = "AIzaSyCGDI006zQ4V0I-GKYVakVkEBD8Gp0JfRI"

with open('/home/dotcloud/environment.json') as f:
    env = json.load(f)

connection = pymongo.MongoClient(host=env['DOTCLOUD_PREYDB_MONGODB_HOST'], port=int(env['DOTCLOUD_PREYDB_MONGODB_PORT']))
db = connection.preydb
db.authenticate(env['PREYDB_USER'], env['PREYDB_PWD'])
users_collection = db.users


@app.route('/')
def homepage():
    print >> sys.stderr, "HOMEPAGE!"
    return render_template('homepage.html')


#Don't use yet
@app.route('/users.xml', methods=['POST'])
def users():
    if request.method == 'POST':
        keyvalue = prey_params_dict(request.data)
        print_stderr("POST Data (users.xml): " + str(keyvalue))

        user_dict = dict(dict.fromkeys(['name', 'email', 'pwd'], None))

        result = "<errors><error>%s</error><errors>"

        if "user%5Bname%5D" in keyvalue:
            user_dict['name'] = keyvalue["user%5Bname%5D"]
        if "user%5Bemail%5D" in keyvalue:
            user_dict['email'] = keyvalue["user%5Bemail%5D"]
        if "user%5Bpassword%5D" in keyvalue:
            user_dict['pwd'] = keyvalue["user%5Bpassword%5D"]

        if all(x is not None for x in user_dict):
                #VERIFY PWD ETC
                user_id = users_collection.find_one({"email": user_dict['email']})  # , fields=["_id"])
                print_stderr("User ID: " + str(user_id))
                if user_id is None:
                    #USER DOES NOT EXIST
                    print_stderr("USer does not exist")
                    user_dict['salt'] = uuid.uuid4().bytes
                    #user_dict['salt'] = "ejfn8w4yrw3y23478yfehf234y"
                    print_stderr(user_dict['salt'])
                    print_stderr(hashlib.sha512(user_dict['pwd'] + user_dict['salt']))
                    user_dict['pwd'] = hashlib.sha512(user_dict['pwd'] + user_dict['salt']).digest()
                    print_stderr(user_dict['pwd'])
                    #I am sure this is a really bad idea (api_key is also the salt)
                    user_dict['api_key'] = user_dict['salt']
                    users_collection.insert(user_dict)

                    result = "<key>" + user_dict['salt'] + "</key>"

                else:
                    result = result % ("That email address is already registered")

        else:
            result = result % ("Please enter valid details")

        print_stderr(result)
        return result


"""This stuff's all hardcoded for now"""
@app.route('/devices.xml', methods=['POST'])
def devices():
    if request.method == 'POST':
        keyvalue = prey_params_dict(request.data)

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
        calls_module = ET.SubElement(modules, "module",
                attrib={"type":"report", "active": "true",
                    "name": "calls", "version": "1.5"})

        print_stderr(tostring(root))
        return tostring(root)

    elif request.method == 'POST':
        #pairs = request.data.split("&")
        #keyvalue = {f[0]: f[1] for f in [x.split("=") for x in pairs]}
        keyvalue = prey_params_dict(request.data)


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


@app.route('/devices/<device_id>/reports.xml', methods=['GET', 'POST'])
def reports(device_id):
    if request.method == 'GET':
        print_stderr("Get params (devices/[id].xml):" + str(request.args.items()))
    elif request.method == 'POST':
        print_stderr("Post Data (devices/[id].xml):" + str(request.data))
    #elif request.method == 'PUT':
    #    print_stderr("Put Data (devices/[id].xml):" + str(request.data))
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


def prey_params_dict(prey_params):
        pairs = prey_params.split("&")
        return {f[0]: f[1] for f in [x.split("=") for x in pairs]}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
