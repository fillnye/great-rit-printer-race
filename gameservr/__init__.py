import os

from flask import render_template
from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from enum import Enum
import time
import random
import string
import threading
import json 

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
    END = 2
    INTERROUND = 3
    FAULT = 4

class User:
    def __init__(self, name, id, points):
        self.name = name
        self.id = id
        self.points = points
    def toJSONN(self):
        return {"name":self.name, "id":self.id, "points":self.points}


class Room:
    def __init__(self, users, age):
        self.users = users
        self.age = age
        self.challengecode = "0"
        self.round = 0
        self.status = Status.STARTING
        self.winner = -1

    def mainLoop(self):
        while(self.status!=Status.FAULT):
            if(self.status==Status.STARTING):
                self.startRound()
            elif(self.status==Status.INTERROUND):
                self.startRound()
            elif(self.status==Status.END):
                time.sleep(30)
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
            self.status = Status.END
            user.points+=10
            self.winner = user.id
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
        
        return render_template("user/register.html",foo)

    @app.route('/user/view.html')
    def usrview():
        return render_template("user/view.html")

    @app.route('/roomlist.html')
    def roomlist():
        return render_template("/roomlist.html")

    @app.route('/room/<int:roomid>')
    def room(roomid):
        if(roomone.status==Status.STARTING or roomone.status==Status.INTERROUND):
            return render_template("/room/start.html")
        elif(roomone.status==Status.INROUND):
            return render_template("/room/room.html")
        elif(roomone.status==Status.END):
            return render_template("/room/end.html")
        
        return Response("Internal Server Error", status=500)

    @app.route('/room/<int:roomid>/status')
    def roomstat(roomid):
        userjson = json.dumps(users, default=lambda o: o.__dict__)
        data = {'users':userjson,'status':int(roomone.status.value), 'time':0 }
        return data

    @app.route('/room/<int:roomid>/challenge', methods=['POST'])
    def roomchlg(roomid):
        if request.method == "POST":
            if(('code' in request.form) and roomone.challenge(request.form['code'],roomone.users[0])):
                return redirect('/room/'+str(roomid)) 
            else:
                return redirect('/room/'+str(roomid)+"?fail=true")
                
        return Response("Method Not Allowed", status=405, headers=[('Allow', 'POST')])

    app.add_url_rule("/", endpoint="index")
    return app
