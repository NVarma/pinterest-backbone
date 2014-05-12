"""
Storage interface
"""

import time
import couchdb.client


class Storage(object):
    def __init__(self):
        # initialize our storage, data is a placeholder
        self.data = {}

        # for demo
        self.data['created'] = time.ctime()

    def insert(self, name, value):
        print "---> insert:", name, value
        try:
            self.data[name] = value
            return "added"
        except:
            return "error: data not added"

        # Method for creating Db object to be used globally

    def getDB(self):
        global couch
        couch = couchdb.Server()
        #couch = couchdb
        global mydb
        #mydb = couch['userdb']
        return None

    def insertUser(self, Fname, Lname, emailId, password):
        couch = couchdb.Server()
        mydb = couch['userdb']
        print Fname
        doc_id, doc_rev = mydb.save({'Fname': Fname, 'Lname': Lname, 'emailID': emailId, 'password': password})
        print doc_id
        dbid = mydb[doc_id].id
        print dbid
        return dbid


    def insertBoard(self, user_id, bname, bdesc, bcategory, bType):
        couch = couchdb.Server()
        mydb = couch['boards']
        print bname
        doc_id, doc_rev = mydb.save(
            {'user_id': user_id, 'boardName': bname, 'boardDescription': bdesc, 'boardCategory': bcategory,
             'boardType': bType})
        db_id = mydb[doc_id].id
        return db_id


    #update board

    def updateBoard(self, user_id, bName, bname, bdesc, bcategory, bType):
        couch = couchdb.Server()
        mydb = couch['boards']
        print bname
        doc = mydb[bName]
        doc['boardName'] = bname
        doc['boardDescription'] = bdesc
        doc['boardCategory'] = bcategory
        doc['boardType'] = bType
        mydb[bName] = doc



        #doc_id,doc_rev = mydb.save({'user_id':user_id,'boardName':bname,'boardDescription':bdesc,'boardCategory':bcategory,'boardType':bType})
        #doc_id,doc_rev = mydb.update({'user_id':user_id,'boardName':bname,'boardDescription':bdesc,'boardCategory':bcategory,'boardType':bType})
        # db_id= mydb[doc_id].id
        # doc=mydb[doc_id]

        # mydb[doc.id]=doc
        return bName


    def deleteBoard(self, user_id, bName):
        couch = couchdb.Server()
        mydb = couch['boards']
        print bName
       # doc = mydb[bName]
        del mydb[bName]


# region Description
# def remove(self,name):
#       print "---> remove:",name
#
#    def names(self):
#       print "---> names:"
#       for k in self.data.iterkeys():
#         print 'key:',k
#
#    def find(self,name):
#       print "---> storage.find:",name
#       if name in self.data:
#          rtn = self.data[name]
#          print "---> storage.find: got value",rtn
#          return rtn
#       else:
#          return None
# endregion
