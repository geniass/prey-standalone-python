# -*- coding: utf8 -*-

from flask import Flask, render_template, redirect, url_for, g, request
import sys

app = Flask(__name__)

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


@app.route('/devices.xml', methods=['POST'])
def devices():
    if request.method == 'POST':
        pairs = request.data.split("&")

        keyvalue = {f[0]: f[1] for f in [x.split("=") for x in pairs]}

        print_stderr("Request Data (devices.xml):" + str(keyvalue))

        return """<?xml version="1.0" encoding="UTF-8"?>
                    <device><key>akf7ef</key></device>"""


@app.route('/profile.xml', methods=['GET'])
def profile():
    if request.method == 'GET':
        #ADD HTTP BASIC AUTH
        print_stderr(request.data)
        print_stderr(request.args.items())
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
