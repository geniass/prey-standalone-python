from flask import Flask, render_template, redirect, url_for, g, request

app = Flask(__name__)

@app.route('/')
def homepage():
    app.logger.debug("HOMEPAGE!")
    return render_template('homepage.html')


@app.route('/users.xml', methods=['POST'])
def users():
    if request.method == 'POST':
        app.logger.debug(request.data)


@app.route('/devices.xml', methods=['POST'])
def devices():
    if request.method == 'POST':
        app.logger.debug(request.data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)