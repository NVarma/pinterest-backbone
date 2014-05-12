"""
6, Apr 2013

Example bottle (python) RESTful web service.

This example provides a basic setup of a RESTful service

Notes
1. example should perform better content negotiation. A solution is
   to use minerender (https://github.com/martinblech/mimerender)
"""

import time
import sys
import socket
import json
import couchdb

# bottle framework
from bottle import request, response,put, route, run, template

# moo
from classroom import Room
from data.storage import Storage
# virtual classroom implementation
room = None


def setup(base, conf_fn):
    print '\n**** service initialization ****\n'
    global room
    room = Room(base, conf_fn)


#
# setup the configuration for our service
@route('/')
def root():
    print "--> root"
    return 'welcome'


#
#
@route('/moo/ping', method='GET')
def ping():
    return 'ping %s - %s' % (socket.gethostname(), time.ctime())


#
# Development only: echo the configuration of the virtual classroom.
#
# Testing using curl:
# curl -i -H "Accept: application/json" http://localhost:8080/moo/conf
#
# WARN: This method should be disabled or password protected - dev only!
#
@route('/moo/conf', method='GET')
def conf():
    fmt = __format(request)
    response.content_type = __response_format(fmt)
    return room.dump_conf(fmt)


#
# example of a RESTful method. This example is very basic, it does not 
# support much in the way of content negotiation.
#
@route('/moo/echo/:msg')
def echo(msg):
    fmt = __format(request)
    response.content_type = __response_format(fmt)
    if fmt == Room.html:
        return '<h1>%s</h1>' % msg
    elif fmt == Room.json:
        rsp = {}
        rsp["msg"] = msg
        return json.dumps(all)
    else:
        return msg


#
# example of a RESTful query
#
@route('/moo/data/:name', method='GET')
def find(name):
    print '---> moo.find:', name
    return room.find(name)


#
# example adding data using forms
#
@route('/moo/data', method='POST')
def add():
    print '---> moo.add'

    # example list form values
    for k, v in request.forms.allitems():
        print "form:", k, "=", v

    name = request.forms.get('name')
    value = request.forms.get('value')
    return room.add(name, value)


#
# Sign-up functionality
#   
@route('/users/signUp', method='POST')
def signUp():
    print '---> moo.signUp'
    Fname = request.POST.get('fname')
    Lname = request.POST.get('lname')
    emailId = request.POST.get('emailId')
    password = request.POST.get('password')
    global storage
    storage = Storage()
    user_id = storage.insertUser(Fname, Lname, emailId, password)
    return user_id


#create board

@route('/users/:id/boards', method='POST')
def createBoard(id):
    print '--in moo.createBoard'
    user_id = request.forms.get("id")
    print "id", user_id

    couch = couchdb.Server()
    mydb = couch['userdb']
    #doc = mydb[user_id]
    if user_id in mydb:
        bname = request.POST.get('boardName')
        bdesc = request.POST.get('boardDesc')
        category = request.POST.get('category')
        boardType = request.POST.get('isPrivate')

        global storage
        storage = Storage()
        boardId = storage.insertBoard(user_id, bname, bdesc, category, boardType)
        return boardId
    else:
        return "User not Authorized!"





# update board

@route('/users/:id/boards/:boardName', method='PUT')
def updateBoard(id,boardName):
    print '--in moo.createBoard'
    user_id = request.forms.get("id")
    bName=request.forms.get("boardName")
    print "id", user_id
    print "boardName", bName


    couch = couchdb.Server()
    mydb = couch['userdb']
    myboardDB = couch['boards']

    #doc = mydb[user_id]
    if user_id in mydb:
        if bName in myboardDB:
        # bname=request.PUT.get('boardName')
        # bdesc = request.PUT.get('boardDesc')
        # category = request.PUT.get('category')
        # boardType = request.PUT.get('isPrivate')

            bname = request.POST.get('name')
            bdesc = request.POST.get('boardDesc')
            category = request.POST.get('category')
            boardType = request.POST.get('isPrivate')
            print "new board name is ", bname
            global storage
            storage = Storage()
            boardId = storage.updateBoard(user_id,bName, bname, bdesc, category, boardType)
            return boardId
        else:
            return "Board not Authorized!"
    else:
        return "User not authorized"




# delete board

@route('/users/:id/boards/:boardName', method='DELETE')
def deleteBoard(id,boardName):
    print '--in moo.deleteBoard'
    user_id = request.forms.get("id")
    bName=request.forms.get("boardName")
    print "id", user_id
    print "boardName", bName
    couch = couchdb.Server()
    mydb = couch['userdb']
    myboardDB = couch['boards']

    #doc = mydb[user_id]
    if user_id in mydb:
        if bName in myboardDB:
            global storage
            storage = Storage()
            boardId = storage.deleteBoard(user_id,bName)

        else:
            return "Board not Authorized!"
    else:
        return "User not authorized"


@route('/users/:id/board/:boardId', method='GET')
def getBoardList(id):
    print '--in moo.createBoard'
    user_id = request.forms.get("id")
    board_id=request.forms.get("boardId")
    print "id", user_id

    couch = couchdb.Server()
    myUserdb = couch['userdb']
    mydb = couch['boards']
    doc = mydb.get(board_id)
    print "The value is ", doc
    print myUserdb

    #if user_id in myUserdb:
      #  print "User"
    #else:
     #   return "User not Authorized!"



#
# Determine the format to return data (does not support images)
#
# TODO method for Accept-Charset, Accept-Language, Accept-Encoding, 
# Accept-Datetime, etc should also exist
#
def __format(request):
    #for key in sorted(request.headers.iterkeys()):
    #   print "%s=%s" % (key, request.headers[key])

    types = request.headers.get("Accept", '')
    subtypes = types.split(",")
    for st in subtypes:
        sst = st.split(';')
        if sst[0] == "text/html":
            return Room.html
        elif sst[0] == "text/plain":
            return Room.text
        elif sst[0] == "application/json":
            return Room.json
        elif sst[0] == "*/*":
            return Room.json

            # TODO
            # xml: application/xhtml+xml, application/xml
            # image types: image/jpeg, etc

    # default
    return Room.html


#
# The content type on the reply
#
def __response_format(reqfmt):
    if reqfmt == Room.html:
        return "text/html"
    elif reqfmt == Room.text:
        return "text/plain"
    elif reqfmt == Room.json:
        return "application/json"
    else:
        return "*/*"

        # TODO
        # xml: application/xhtml+xml, application/xml
        # image types: image/jpeg, etc
