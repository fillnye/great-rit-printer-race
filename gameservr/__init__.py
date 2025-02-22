import os

from flask import render_template
from flask import Flask
from flask import request
from enum import Enum
import time
import random
import string
import threading

#from pymongo.mongo_client import MongoClient
#from pymongo.server_api import ServerApi

#uri = "mongodb+srv://gjl1803:gYJg69YkajZzqh7D@greatritprinterrace.yqz1e.mongodb.net/?retryWrites=true&w=majority&appName=GreatRITPrinterRace"
#
# Create a new client and connect to the server
#client = MongoClient(uri, server_api=ServerApi('1'))
#
# Send a ping to confirm a successful connection
#try:
#    client.admin.command('ping')
#    print("Pinged your deployment. You successfully connected to MongoDB!")
#except Exception as e:
#    print(e)

class Status(Enum):
    STARTING = 0
    INROUND = 1
    INTERROUND = 2
    FAULT = 3

class User:
    def __init__(self, name, id, points):
        self.name = name
        self.id = id
        self.points = points


class Room:
    def __init__(self, users, age):
        self.users = users
        self.age = age
        self.challengecode = "0"
        self.round = 0
        self.status = Status.STARTING

    def mainLoop(self):
        while(self.status!=Status.FAULT):
            if(self.status==Status.STARTING):
                self.startRound()
            elif(self.status==Status.INTERROUND):
                self.startRound()
            
    def startRound(self):
        if(len(self.users)<1):
            print("NOT ENOUGHT USERS TO START")
            time.sleep(10)
            return
        self.challengecode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.printcode()
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
    users=[User("Bob",32,500),User("Bob2",33,500),User("Bil",35,510)]
    roomone = Room(users,0)

    gamethread = threading.Thread(target=roomone.mainLoop)

    gamethread.start()
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
    
    @app.route('/user/edit.html')
    def usredit():
        return render_template("user/edit.html")

    @app.route('/room/join.html')
    def joinroom():
        return render_template("room/join.html")

    @app.route('/room/<int:roomid>')
    def room(roomid):
        return render_template("room/room.html")

    @app.route('/room/<int:roomid>/status')
    def roomstat(roomid):
        return 

    @app.route('/room/<int:roomid>/challenge>')
    def roomchlg(roomid):
        if request.method == "POST":
            return
        return

    app.add_url_rule("/", endpoint="index")
    return app
