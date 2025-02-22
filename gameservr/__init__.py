import os

from flask import render_template
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/index.html')
    def hello():
        return render_template("index.html");

    return app
