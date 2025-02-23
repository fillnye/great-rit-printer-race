import os

from flask import render_template
from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import session
from enum import Enum
import time
import random
import string
import threading
import json


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://gjl1803:gYJg69YkajZzqh7D@greatritprinterrace.yqz1e.mongodb.net/?retryWrites=true&w=majority&appName=GreatRITPrinterRace"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.BrickHack11

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

class Status(Enum):
    STARTING = 0
    INROUND = 1
    END = 2
    INTERROUND = 3
    FAULT = 4

class User:
    def __init__(self, name, points):
        self.name = name
        self.points = points
    def toJSONN(self):
        return {"name":self.name, "points":self.points}


class Room:
    def __init__(self, users, age):
        self.users = users
        self.age = age
        self.challengecode = "0"
        self.round = 0
        self.status = Status.STARTING
        self.winner = "No One"
        self.timeleft = 0;
        self.round = 0;

    def mainLoop(self):
        while(self.status!=Status.FAULT):
            if(self.status==Status.STARTING):
                self.startRound()
            elif(self.status==Status.INTERROUND):
                self.startRound()
                print("e")
            elif(self.  status==Status.INROUND):
                self.timeleft = 600
                print("o")
                self.winner="No One"
                while(self.timeleft>0):
                    time.sleep(1)
                    self.timeleft -= 1
                    if(self.status==Status.END):
                        break                
                self.timeleft = 30                
                self.status=Status.END
            elif(self.status==Status.END):
                while(self.timeleft>0):
                    time.sleep(1)
                    self.timeleft -= 1
                self.status=Status.INTERROUND
            
    def startRound(self):
        if(len(self.users)<1):
            print("NOT ENOUGH USERS TO START")
            self.timeleft = 10
            while(self.timeleft>0):
                time.sleep(1)
                self.timeleft -= 1
            return
        self.challengecode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.printcode()
        self.round+=1
        self.status = Status.INROUND
    def printcode(self):
        print(self.challengecode)
    def challenge(self,challengecode,user):
        if(challengecode==self.challengecode):
            user.points+=10
            self.winner = user.name
            self.status = Status.END
            return True
        else:
            return False


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    users = {}
    roomone = Room(users,0)

    gamethread = threading.Thread(target=roomone.mainLoop)

    gamethread.start()
    def userCheck():
        if 'username' in session:
            return session['username']
        return None

    # a simple page that says hello
    @app.route('/index')
    def index():
        return render_template("index.html")
    @app.route('/user/login', methods=['POST','GET'])
    def login():
        if request.method == "POST":
            user = db.users.find_one({'name':request.form['username']})
            if(user!=None):
                session['username'] = request.form['username']
                users[request.form['username']] = user
                print(session) # TODO delete this 
                return redirect("../room/join")
        return render_template("user/login.html")
    @app.route('/user/logout')
    def logout():
        username = userCheck()
        session.pop('username', None)
        if username in users:
            users.pop(username)
        return redirect("../index")
    @app.route('/user/register', methods=['POST','GET'])
    def reg():
        if request.method == "POST":
            user = db.users.find_one({'name':request.form['username']})
            if(user==None):
                db.users.insert_one({'name':request.form['username'],'points':0})
                return redirect("/user/login")
        return render_template("user/register.html")

    @app.route('/user/view')
    def usrview():
        username = userCheck()
        user = db.users.find_one({'name':username})
        if(user!=None):
            return render_template("user/view.html", user=user)
        else:
            return logout()

    @app.route('/roomlist')
    def roomlist():
        #userCheck()
        return render_template("/roomlist.html")

    @app.route('/room/<int:roomid>')
    def room(roomid):
        #userCheck()
        if(roomone.status==Status.STARTING or roomone.status==Status.INTERROUND):
            return render_template("/room/start.html",timeleft=roomone.timeleft,round=roomone.round,room=roomid)
        elif(roomone.status==Status.INROUND):
            return render_template("/room/room.html",timeleft=roomone.timeleft,round=roomone.round,room=roomid)
        elif(roomone.status==Status.END):
            return render_template("/room/end.html",winner=roomone.winner,timeleft=roomone.timeleft,round=roomone.round,room=roomid)
        
        return Response("Internal Server Error", status=500)

    @app.route('/room/<int:roomid>/status')
    def roomstat(roomid):
        userjson = json.dumps(users, default=lambda o: o.__dict__)
        data = {'users':userjson,'status':int(roomone.status.value), 'time':roomone.timeleft }
        return data

    @app.route('/room/<int:roomid>/challenge', methods=['POST'])
    def roomchlg(roomid):
        if request.method == "POST":
            if(('code' in request.form) and roomone.challenge(request.form['code'],roomone.users[0])):
                roomone.timeleft = 30
                return redirect('/room/'+str(roomid)) 
            else:
                return redirect('/room/'+str(roomid)+"?fail=true")
                
        return Response("Method Not Allowed", status=405, headers=[('Allow', 'POST')])

    app.add_url_rule("/", endpoint="index")
    return app
