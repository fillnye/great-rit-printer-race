import os

from flask import render_template
from flask import Flask
from enum import Enum
import time

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://gjl1803:gYJg69YkajZzqh7D@greatritprinterrace.yqz1e.mongodb.net/?retryWrites=true&w=majority&appName=GreatRITPrinterRace"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

class Status(Enum):
    STARTING = 0
    INROUND = 1
    INTERROUND = 2
    FAULT = 3

class User:
    def __init__(self, users, age):
        self.name = name
        self.id = age
        self.points = 0


class Room:
    def __init__(self, users, age):
        self.users = users
        self.age = age
        self.challengecode = "0"
        self.round = 0
        self.status = Status.STARTING

    def mainLoop(self):
        while(self.status!=FAULT):
            if(self.status==STARTING):
                startRound(self)
            elif(self.status==INTERROUND):
                startRound(self)
            
    def startRound(self):
        if(len(self.users)<1):
            print("NOT ENOUGHT USERS TO START")
            time.sleep(40)
            return
        self.challengecode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        printcode()
        self.status = Status.INROUND
    def printcode(self):
        print(self.challengecode)
    def challenge(self,challengecode,user):
        if(challengecode==self.challengecode):
            self.status = Status.INTERROUND
            user.points+=10
            return True
        else:
            return False


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/index.html')
    def index():
        return render_template("index.html")

    @app.route('/user/register.html')
    def reg():
        if request.method == "POST":
            #Proccses reg data
            return "Succses"
        
        return render_template("user/register.html")

    @app.route('/user/view.html')
    def usrview():
        return render_template("user/view.html")

    @app.route('/room/join.html')
    def joinroom():
        return render_template("user/edit.html")

    @app.route('/room/<int:roomid>')
    def room(roomid):
        return render_template("user/edit.html")

    @app.route('/room/<int:roomid>/status')
    def roomstat(roomid):
        return 

    @app.route('/room/<int:roomid/challenge>')
    def roomchlg(roomid):
        if request.method == "POST":
            return
        return

    app.add_url_rule("/", endpoint="index")
    return app
