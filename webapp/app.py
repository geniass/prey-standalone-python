# -*- coding: utf8 -*-

from flask import Flask, render_template, redirect, url_for, request, Response, flash, g
from flask.ext.login import *
from User import User
from Forms import LoginForm
import sys
import requests
import elementtree.ElementTree as ET
from elementtree.ElementTree import tostring
import json
import pymongo
from bson.objectid import ObjectId
import bcrypt
import uuid
import string
import random
import datetime
from urllib2 import quote, unquote

app = Flask(__name__)

GCM_URL = "https://android.googleapis.com/gcm/send"
API_KEY = "AIzaSyCGDI006zQ4V0I-GKYVakVkEBD8Gp0JfRI"

# this will load environment variables from dotcloud. If it is running on
# localhost, it will do whatever is in the 'except' part
try:
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)

        #connection = pymongo.MongoClient(host=env['DOTCLOUD_PREYDB_MONGODB_HOST'], port=int(env['DOTCLOUD_PREYDB_MONGODB_PORT']))
        connection = pymongo.MongoClient(env['PREYDB_URL'])
        #db.authenticate(env['PREYDB_USER'], env['PREYDB_PWD'])

        # have to convert from unicode to string otherwise shit happens
        app.secret_key = str(env['SECRET_KEY'])

except IOError:
    # connect to localhost mongodb
    connection = pymongo.MongoClient()
    # this key is only used locally so it doesn't matter if you know it
    # have to convert from unicode to string otherwise shit happens
    app.secret_key = str("""D"vl<K,E[;#^.!Re/Z|hnLG)$Ngkyc,oN\.%Z;J(uKSTV)ztVAjg*i]O$9|{@;;""")

db = connection.preydb
users_collection = db.users
devices_collection = db.devices
reports_collection = db.reports

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    _id = ObjectId(userid.encode('utf-8'))
    user = users_collection.find_one(_id)
    return User(user['email'], _id, True)


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def homepage():
    devices = devices_collection.find()
    return render_template('index.html', devices=devices)


@app.route('/reports')
@login_required
def reports_page():
    devices = devices_collection.find()
    return render_template('reports-devices.html', devices=devices)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect('/')
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_dict = users_collection.find_one({"email": login_form.email.data})
        if not user_dict:
            flash("That email has not been registered")
            return redirect('/signup')
        pwd_hash = bcrypt.hashpw(login_form.password.data, user_dict['salt'])
        if pwd_hash == user_dict['pwd']:
            user = User(user_dict['email'], user_dict['_id'])
            login_user(user, remember=login_form.remember_me.data)
            flash("Logged in succesfully")
            return redirect('/')
        else:
            flash("The password you entered is incorrect")
            return redirect('/login')
    return render_template('login.html', login_form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


#Don't use yet
@app.route('/users.xml', methods=['POST'])
def users():
    if request.method == 'POST':
        print_stderr("Users.xml Request.data: " + str(request.data))
        print_stderr("Users.xml Other thing: " + str(request.form.keys()))

        keyvalue = prey_params_dict(request.data)
        print_stderr("POST Data (users.xml): " + str(keyvalue))

        user_dict = dict(dict.fromkeys(['name', 'email', 'pwd'], None))

        result = "<errors><error>%s</error><errors>"

        if "user%5Bname%5D" in keyvalue:
            user_dict['name'] = unquote(keyvalue["user%5Bname%5D"])
        if "user%5Bemail%5D" in keyvalue:
            user_dict['email'] = unquote(keyvalue["user%5Bemail%5D"])
        if "user%5Bpassword%5D" in keyvalue:
            user_dict['pwd'] = unquote(keyvalue["user%5Bpassword%5D"])

        if all(x is not None for x in user_dict):
                #VERIFY PWD ETC
                user_id = users_collection.find_one(
                        {"email": user_dict['email']})  # , fields=["_id"])
                print_stderr("User ID: " + str(user_id))
                if user_id is None:
                    #USER DOES NOT EXIST
                    user_dict['salt'] = bcrypt.gensalt()
                    user_dict['pwd'] = bcrypt.hashpw(user_dict['pwd'],
                                                    user_dict['salt'])
                    user_dict['api_key'] = uuid.uuid4().hex
                    users_collection.insert(user_dict)

                    result = "<key>" + user_dict['api_key'] + "</key>"

                else:
                    result = result % ("That email address is already registered")

        else:
            result = result % ("Please enter valid details")

        print_stderr(result)
        return result


"""This stuff's all hardcoded for now
Crap, nothing stops someone from ading a device to someone else's
account. Oh well"""
@app.route('/devices.xml', methods=['POST'])
def devices():
    if request.method == 'POST':
        if not request.data:
            data = request.form.keys()[0]
        else:
            data = request.data

        print_stderr("POST data (devices.xml): " + str(data))

        keyvalue = prey_params_dict(data)
        device = {}
        device_id = None

        print_stderr("Request Data (devices.xml):" + str(keyvalue))

        #Holy shit
        while True:
            device_id = random_string(5)
            if devices_collection.find_one({"device_id": device_id}) is None:
                if "device%5Bmodel_name%5D" in keyvalue:
                    device['model'] = keyvalue["device%5Bmodel_name%5D"]
                if "device%5Bvendor_name%5D" in keyvalue:
                    device['vendor'] = keyvalue["device%5Bvendor_name%5D"]
                if "device%5Bactivation_phrase%5D" in keyvalue:
                    device['activation_phrase'] = keyvalue["device%5Bactivation_phrase%5D"].replace("%20", " ")
                if "device%5Bdeactivation_phrase%5D" in keyvalue:
                    device['deactivation_phrase'] = keyvalue["device%5Bdeactivation_phrase%5D"].replace("%20", " ")
                if "device%5Bos_version%5D" in keyvalue:
                    device['os_version'] = keyvalue["device%5Bos_version%5D"]
                if "device%5Bos%5D" in keyvalue:
                    device['os'] = keyvalue["device%5Bos%5D"]
                if "api_key" in keyvalue:
                    device['api_key'] = keyvalue["api_key"]
                if "device%5Bphysical_address%5D" in keyvalue:
                    device['imei'] = keyvalue["device%5Bphysical_address%5D"]

                device['device_id'] = device_id
                device['missing'] = False
                devices_collection.save(device)

                break

        return """<?xml version="1.0" encoding="UTF-8"?>
                    <device><key>""" + device_id + """</key></device>"""


@app.route('/devices/<device_id>.xml', methods=['GET', 'POST', 'DELETE'])
def device(device_id):
    if request.method == 'GET':
        print_stderr("Get params (devices/[id].xml):" + str(request.args.items()))
        root = ET.Element("device")

        status = ET.SubElement(root, "status")
        missing = ET.SubElement(status, "missing")
        missing.text = "true"   # True because it only GETs this page if it is missing
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
                attrib={"type": "report", "active": "true",
                    "name": "network", "version": "1.5"})

        geo_module = ET.SubElement(modules, "module",
                attrib={"type": "report", "active": "true",
                    "name": "geo", "version": "1.5"})
        #calls_module = ET.SubElement(modules, "module",
        #        attrib={"type":"report", "active": "true",
        #            "name": "calls", "version": "1.5"})

        print_stderr(tostring(root))
        return tostring(root)

    elif request.method == 'POST':
        keyvalue = prey_params_dict(request.data)
        device = {}

        print_stderr("Post Data (devices/[id].xml):" + str(keyvalue))

        if 'device%5Bnotification_id%5D' in keyvalue:
            device['notification_id'] = keyvalue['device%5Bnotification_id%5D']
            print_stderr("REG: " + str(device['notification_id']))
        if 'device%5Bmissing%5D' in keyvalue:
            device['missing'] = keyvalue['device%5Bmissing%5D']
            print_stderr("Device missing changed to: " + device['missing'])
        if 'api_key' in keyvalue:
            device['api_key'] = keyvalue['api_key']

        _id = devices_collection.find_one({"api_key": device['api_key'],
                                            "device_id": device_id})['_id']
        if _id is not None:
            print_stderr("Updating DB: " + str(device))
            devices_collection.update({"_id": _id}, {"$set": device}, upsert=True)

    elif request.method == 'DELETE':
        print_stderr("DELETE Data (devices/[id].xml):" + str(request.data))
        devices_collection.remove({"device_id": device_id})

    return "<data></data>"


@app.route('/devices/<device_id>/reports.xml', methods=['GET', 'POST'])
def reports_xml(device_id):
    if request.method == 'GET':
        device = devices_collection.find_one({"device_id": device_id})
        user = users_collection.find_one(g.user._id)
        if device['api_key'] == user['api_key']:
            reports = reports_collection.find({'device_id': device_id})
            print_stderr(reports[0])
            return render_template('reports_basic.html', reports=reports)
        else:
            flash("Editing URL's? That's not your device!")
            return redirect('/')

    elif request.method == 'POST':
        print_stderr("reports.xml")
        print_stderr("Post Data (devices/[id].xml):" + str(request.data))
        if not request.data:
            data = request.form.keys()[0]
        else:
            data = request.data

        keyvalue = prey_params_dict(data)

        report = {}

        #GEO LOCATION
        if 'geo%5Blat%5D' in keyvalue:
            report['latitude'] = keyvalue['geo%5Blat%5D']
        if 'geo%5Blng%5D' in keyvalue:
            report['longitude'] = keyvalue['geo%5Blng%5D']
        if 'geo%5Balt%5D' in keyvalue:
            report['altitude'] = keyvalue['geo%5Balt%5D']
        if 'geo%5Bacc%5D' in keyvalue:
            report['accuracy'] = keyvalue['geo%5Bacc%5D']

        report['utc_time'] = datetime.datetime.utcnow()

        report['device_id'] = device_id

        reports_collection.save(report)

    #elif request.method == 'PUT':
    #    print_stderr("Put Data (devices/[id].xml):" + str(request.data))
    return "<data></data>"


@app.route('/getreport')
def getreport():
    if request.method == 'GET':
        params = request.args
        print_stderr("Get params (getreport):" + str(request.args.items()))
        if 'id' in params:
            report = reports_collection.find_one({"_id": ObjectId(params['id'])})
            report['_id'] = str(report['_id'])
            report['utc_time'] = str(report['utc_time'])
            print_stderr(report)
            return Response(json.dumps(report), mimetype='text/json')


#Needs some authentication
@app.route('/devices/<device_id>/missing')
def missing(device_id):
    device = devices_collection.find_one({"device_id": device_id})
    print_stderr(device)

    if device is not None:
        regId = device['notification_id']

        print_stderr("Reg ID: " + str(regId))
        headers = {"content-type": "application/json",
                        "Authorization": "key=" + str(API_KEY)}
        payload = {"registration_ids": [regId],
                "data": {"data": {"event": "message",
                        "data": {"type": "text", "body": "run_once",
                            "key": device_id}}}}

        r = requests.post(GCM_URL, json.dumps(payload), headers=headers)

        return "<div>" + r.text + "</div>"
    else:
        return "<div>This device is not in the database</div>"


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


def random_string(length):
        # Generate random ascii string (5 characters)
        # There are less digits than letters so add digits twice
        return ''.join(random.choice(string.ascii_lowercase + string.digits + string.digits)
                for x in range(length))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
