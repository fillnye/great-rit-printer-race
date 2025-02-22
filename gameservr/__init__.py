import os

from flask import render_template
from flask import Flask
from enum import Enum

class Status(Enum):
    STARTING = 0
    INROUND = 1
    INTERROUND = 3
    FAULT = 4


class room:
    def __init__(self, users, age):
        self.users = users
        self.age = age
        self.challengecode = "0"
        self.status = Status.INROUND
    def startRound():
        if(len(self.users)<1):
            return
        self.challengecode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        print()
        self.status = Status.INROUND
    def print():
        print(self.challengecode)
    def challenge()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/index.html')
    def index():
        return render_template("index.html");

    @app.route('/user/register.html')
    def reg():
        if request.method == "POST":
            #Proccses reg data
            return "Succses"
        
        return render_template("user/register.html");

    @app.route('/user/view.html')
    def usrview():
        return render_template("user/view.html");

    @app.route('/room/join.html')
    def joinroom():
        return render_template("user/edit.html");

    @app.route('/room/<int:roomid>')
    def room(roomid):
        return render_template("user/edit.html");

    @app.route('/room/<int:roomid>/status')
    def room(roomid):
        return 

    @app.route('/room/<int:roomid/challenge>')
    def roomchlg(roomid):
        if request.method == "POST":
        

    app.add_url_rule("/", endpoint="index")
    return app
