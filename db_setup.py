import pymongo


def start():
    client = pymongo.MongoClient("127.0.0.1", 27017)
    mydb = client["voting-service"]
    mydb.command("dropDatabase")
    mydb = client["voting-service"]
    mydb.create_collection("votings")
    # mydb["votings"].create_index([('voting_id', pymongo.ASCENDING)])
    mydb.create_collection("users")
    mydb["users"].create_index([('username', pymongo.ASCENDING)], unique=True)
    mydb["users"].insert_one({
        'username': 'admin',
        'b64creds': 'YWRtaW46YWRtaW4='
    })
    print(client.list_database_names())
    assert(not list(mydb["votings"].find({})))
    assert len(list(mydb["users"].find({}))) == 1

if __name__ == "__main__":
    start()