import pymongo

'''CONFIG'''

MONGO_URL = "ds057568.mlab.com"
MONGO_PORT = 57568
USERNAME = 'testtest'
PASSWORD = '1amtesting'


def start():
    client = pymongo.MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@ds057568.mlab.com:57568/voting-service?retryWrites=false')
    mydb = client["voting-service"]
    mydb.create_collection("votings")
    mydb["votings"].create_index([('voting_id', pymongo.ASCENDING)])
    mydb.create_collection("users")
    mydb["users"].create_index([('username', pymongo.ASCENDING)], unique=True)
    mydb["users"].insert_one({
        'username': 'admin',
        'b64creds': 'YWRtaW46YWRtaW4='
    })
    assert(not list(mydb["votings"].find({})))
    assert len(list(mydb["users"].find({}))) == 1


if __name__ == "__main__":
    start()