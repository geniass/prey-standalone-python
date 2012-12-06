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
        #app.logger.debug(request.data)
        print_stderr(request.data)


@app.route('/profile.xml', methods=['POST'])
def profile():
    if request.method == 'POST':
        #app.logger.debug(request.data)
        print_stderr(request.data)


@app.route('/reports.xml', methods=['POST'])
def reports():
    if request.method == 'POST':
        #app.logger.debug(request.data)
        print_stderr(request.data)



def print_stderr(message):
    print >> sys.stderr, message


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
