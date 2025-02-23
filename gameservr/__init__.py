from flask import render_template
from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import session
from flask import abort
from enum import Enum
import time
import random
import string
import threading
import json
import cups
import random
import subprocess

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
    def __init__(self,cupsconn):
        self.users = []
        self.timeout = []
        self.challengecode = "0"
        self.round = 0
        self.status = Status.STARTING
        self.winner = "No One"
        self.timeleft = 0
        self.round = 0
        self.cupsconn = cupsconn

    def mainLoop(self):
        while(self.status!=Status.FAULT):
            if(self.status==Status.STARTING):
                self.startRound()
            elif(self.status==Status.INTERROUND):
                self.startRound()
            elif(self.  status==Status.INROUND):
                self.timeleft = 600
                self.winner="No One"
                while(self.timeleft>0):
                    self.checkstale()
                    time.sleep(1)
                    self.timeleft -= 1
                    if(self.status==Status.END):
                        break                
                self.timeleft = 30                
                self.status=Status.END
            elif(self.status==Status.END):
                while(self.timeleft>0):
                    self.checkstale()
                    time.sleep(1)
                    self.timeleft -= 1
                self.status=Status.INTERROUND
            
    def startRound(self):
        if(len(self.users)<1):
            print("NOT ENOUGH USERS TO START")
            self.timeleft = 20
            while(self.timeleft>0):
                self.checkstale()
                time.sleep(1)
                self.timeleft -= 1
            return
        self.challengecode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.printcode()
        self.round+=1
        self.status = Status.INROUND
    def printcode(self, ):
        printers = list(self.cupsconn.getPrinters().keys())
        printer = printers[random.randint(0,len(printers)-1)]
        #lpr = subprocess.Popen("/usr/bin/lpr -P"+printer,  stdin=subprocess.PIPE)
        #lpr.stdin.write(str.encode("RIT GREAT PRINTER GAMES CODE:" + self.challengecode))
        print(self.challengecode)
    def challenge(self,challengecode,user,users):
        if(challengecode==self.challengecode):
            users[user]['points']+=10
            self.winner = user
            self.status = Status.END
            return True
        else:
            return False

    def checkstale(self):
        for i in range(0,len(self.users)):
            if (time.time() - self.timeout[i]) > 40:
                self.timeout.pop(i)
                self.users.pop(i)



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    users = {}
    cupsconn = cups.Connection()
    rooms = [Room(cupsconn),Room(cupsconn),Room(cupsconn),Room(cupsconn)]



    for room in rooms:
        gamethread = threading.Thread(target=room.mainLoop)
        gamethread.start()


    def roomCheck(username):
        if users[username]['lastroom']!=-1:
            print("detected:" + username)
            print(users[username]['lastroom'])
            rooms[users[username]['lastroom']].timeout.pop(rooms[users[username]['lastroom']].users.index(username))
            rooms[users[username]['lastroom']].users.remove(username)
            users[username]['lastroom'] = -1


    def userCheck():
        if 'username' in session:
            return session['username']
        return None

    # a simple page that says hello
    @app.route('/index')
    def index():
        username = userCheck()
        user = db.users.find_one({'name': username})
        if (user != None):
            roomCheck(username)
        return render_template("index.html")
    @app.route('/user/login', methods=['POST','GET'])
    def login():
        if request.method == "POST":
            user = db.users.find_one({'name':request.form['username']})
            if(user!=None):
                session['username'] = request.form['username']
                users[request.form['username']] = user
                users[request.form['username']]['lastroom']=-1
                return redirect("../room/list")
            return render_template("user/login.html", fail=True)
        return render_template("user/login.html",fail=False)
    @app.route('/user/logout')
    def logout():
        username = userCheck()
        session.pop('username', None)
        if username in users:
            roomCheck(username)
            users.pop(username)
        return redirect("../index")
    @app.route('/user/register', methods=['POST','GET'])
    def reg():
        if request.method == "POST":
            user = db.users.find_one({'name':request.form['username']})
            if(user==None):
                db.users.insert_one({'name':request.form['username'],'points':0})
                return redirect("/user/login")
            return render_template("user/register.html", fail=True)
        return render_template("user/register.html",fail=False)


    @app.route('/room/list')
    def roomlist():
        username = userCheck()
        user = db.users.find_one({'name': username})
        if (user == None):
            return logout()
        roomCheck(username)
        data = []
        for room in rooms:
            data.append({"round": room.round, "players": len(room.users), "status": room.status.name.lower(),
                         "time": room.timeleft})
        roomjson =  json.dumps(data)
        return render_template("/room/list.html",rooms=rooms, roomjson=roomjson)

    @app.route('/room/list/upd')
    def roomlistupd():
        username = userCheck()
        user = db.users.find_one({'name': username})
        if (user == None):
            return logout()
        roomCheck(username)
        data = []
        for room in rooms:
            data.append({"round":room.round,"players":len(room.users),"status":room.status.name.lower(),"time":room.timeleft})
        return json.dumps(data)


    @app.route('/room/<int:roomid>')
    def room(roomid):
        username = userCheck()
        user = db.users.find_one({'name':username})
        if(user==None):
            return logout()

        if(roomid-1>= len(rooms)):
            return abort(404)

        if (not (username in rooms[roomid].users)):
              rooms[roomid].users.append(username)
              rooms[roomid].timeout.append(time.time())
              roomCheck(username)
              users[username]['lastroom'] = roomid
        else:
            rooms[roomid].timeout[rooms[roomid].users.index(username)] = time.time()
        if(rooms[roomid].status==Status.STARTING or rooms[roomid].status==Status.INTERROUND):
            return render_template("/room/join.html",timeleft=rooms[roomid].timeleft,round=rooms[roomid].round,room=roomid,users=rooms[roomid].users)
        elif(rooms[roomid].status==Status.INROUND):
            fail = request.args.get('fail')
            isFail = not (fail is None)
            return render_template("/room/room.html",timeleft=rooms[roomid].timeleft,round=rooms[roomid].round,room=roomid,users=rooms[roomid].users,isFail=isFail)
        elif(rooms[roomid].status==Status.END):
            return render_template("/room/end.html",winner=rooms[roomid].winner,timeleft=rooms[roomid].timeleft,round=rooms[roomid].round,room=roomid,users=rooms[roomid].users)
        
        return Response("Internal Server Error", status=500)

    @app.route('/room/<int:roomid>/status')
    def roomstat(roomid):
        username = userCheck()
        user = db.users.find_one({'name':username})
        if(user==None):
            data = {'users': "[]", 'status': 8, 'time': 0}
            return data

        if (not (username in rooms[roomid].users)):
            rooms[roomid].users.append(username)
            rooms[roomid].timeout.append(time.time())
            roomCheck(username)
            users[username]['lastroom']=roomid
        rooms[roomid].timeout[rooms[roomid].users.index(username)] = time.time()
        userjson = json.dumps(rooms[roomid].users)
        data = {'users':userjson,'status':int(rooms[roomid].status.value), 'time':rooms[roomid].timeleft }
        return data

    @app.route('/room/<int:roomid>/challenge', methods=['POST'])
    def roomchlg(roomid):
        username = userCheck()
        user = db.users.find_one({'name':username})
        if(user==None):
            return logout()
        rooms[roomid].timeout[rooms[roomid].users.index(username)] = time.time()
        if request.method == "POST":
            if(('code' in request.form) and rooms[roomid].challenge(request.form['code'],username,users)):
                rooms[roomid].timeleft = 30
                return redirect('/room/'+str(roomid)) 
            else:
                return redirect('/room/'+str(roomid)+"?fail=true")
                
        return Response("Internal Server Error", status=500)

    @app.after_request
    def apply_caching(response):
        response.headers["Cache-control"] = "no-cache"
        return response

    app.add_url_rule("/", endpoint="index")
    return app

