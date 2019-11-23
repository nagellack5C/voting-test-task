import base64
from collections import defaultdict
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from bson.errors import InvalidId


'''CONFIG'''

client = MongoClient("127.0.0.1", 27017)
mydb = client["voting-service"]
votings = mydb["votings"]
users = mydb["users"]


def db_create_voting(question: str, options: list, creator: str):
    """
    Create a new voting in database.
    :param question: voting question/topic
    :param options: list of possible answers
    :param creator: username of the voting creator
    :return: id of new voting
    """
    voting = {
        "question": question,
        "options": options,
        "creator": creator
    }
    return str(votings.insert_one(voting).inserted_id)


def db_create_user(username: str, password: str):
    """
    Create a new user in database.
    Password are stored as base64 strings in format {user}:{password}
    :param username: username
    :param password: password
    :return: message to user
    """
    b64creds = b64hash(f'{username}:{password}')
    try:
        users.insert_one(
            {
                "username": username,
                "b64creds": b64creds,
                "votes": {}
            }
        )
        return f'User {username} was successfully created!'
    except DuplicateKeyError:
        return "This username already exists!"


def db_verify_credentials(username: str, password: str):
    """
    Convert provided credentials and look them up in the database.
    :param username: username
    :param password: password
    :return: existence of user and user-password pair
    """
    b64creds = b64hash(f'{username}:{password}')
    return bool(list(users.find({'b64creds': b64creds})))


def db_list_votings(username=None):
    """
    Show all votings in the database.
    :return: dict with all votings
    """
    result = []

    votings_found = list(votings.find({}))
    for voting in votings_found:
        result.append(_get_voting(voting, username))
    return result


def db_view_voting(voting_id: str, username=None):
    """
    Look up and return a single voting with results.
    :param voting_id:
    :param username: username (optional)
    :return:
    """
    try:
        voting = votings.find_one({'_id': ObjectId(voting_id)})
    except InvalidId:
        return 'invalid'
    if voting:
        return _get_voting(voting, username)


def db_vote(username: str, voting_id: str, option: str):
    """
    Vote for one of the options
    :param username: username
    :param voting_id: voting id
    :param option: option to vote for
    :return: voting result
    """
    user = users.find_one({"username": username})
    if not user:
        return "Wrong credentials!"

    try:
        voting = votings.find_one({"_id": ObjectId(voting_id)})
    except InvalidId:
        return "Wrong voting ID format!"
    if not voting:
        return "No such voting!"

    if option not in voting["options"]:
        return 'Wrong option!'

    users.update_one(
        {"username": username},
        {"$set": {f'votes.{voting_id}': option}}
    )

    return "You have successfully voted!"


def _db_delete_user(username: str):
    """
    Delete a single user from database
    :param username: username
    :return: None
    """
    users.remove({"username": username})


def db_delete_voting(voting_id: str, username: str):
    """
    Delete a voting from database
    :param voting_id: voting id
    :param username: username
    :return: 'invalidid' or deleted count
    """
    try:
        x = votings.delete_one(
            {
                "_id": ObjectId(voting_id),
                'creator': {'$in': (username, 'admin')}
            }
        )
    except InvalidId:
        return 'invalid'
    if x.deleted_count:
        _purge_votes(voting_id, voting_removed=True)
    print(x.deleted_count)
    return x.deleted_count


def db_update_voting(voting_id: str, username: str, question=None, options=None):
    """
    Update a single voting with new question and/or options, then
    remove existing votes if matching options had been deleted.
    :param voting_id: voting id
    :param username: username
    :param question: voting question
    :param options: list of voting options
    :return: invalid id or update status
    """
    try:
        voting = votings.find_one({'_id': ObjectId(voting_id)})
    except InvalidId:
        return 'invalid'
    updated = None
    if voting and voting['creator'] in (username, 'admin'):
        update = {}
        if question:
            update["question"] = question
        if options:
            update["options"] = options
        if update:
            updated = votings.update_one(
                {'_id': voting['_id']},
                {
                    '$set': update
                }
            ).matched_count
        if options and updated:
            _purge_votes(voting["_id"], voting["options"], options)
    return bool(updated)


''' SERVICE FUNCTIONS '''


def _purge_votes(voting_id: str, old_options=None, new_options=None, voting_removed=False):
    """
    Service function that looks ups and delete votes when votings are changed
    or removed, can't be accessed from the front-end directly.
    :param voting_id: voting id
    :param old_options: list of options before voting update
    :param new_options: list of options after voting update
    :param voting_removed: voting removal status
    :return: None
    """
    deletable_options = None
    if old_options and new_options:
        deletable_options = set(old_options) - set(new_options)

    if voting_removed:
        users.update_many(
            {
                f'votes.{voting_id}': {
                    '$exists': True
                }
            },
            {
                '$unset': {f'votes.{voting_id}': 1}
            }
        )
    elif deletable_options:
        users.update_many(
            {
                f'votes.{voting_id}': {
                    '$in': list(deletable_options)
                }
            },
            {
                '$unset': {f'votes.{voting_id}': 1}
            }
        )


def _get_voting(voting: dict, username=None):
    """
    Service function that creates a dict with voting information.
    Can't be accessed from the front-end directly.
    :param voting: voting dict
    :param username: username
    :return: dict with voting info
    """
    voters = list(users.find(
        {
            f'votes.{voting["_id"]}': {'$exists': True}
        },
        {'votes': 1, '_id': 0}
    ))
    voting_results = defaultdict(int)
    for voter in voters:
        vote_option = voter['votes'][str(voting["_id"])]
        voting_results[vote_option] += 1

    total = sum(voting_results.values())

    voting_percents = _calculate_voting_percents(voting_results, total)

    user_vote = None
    if username:
        user_vote = search_user_vote(str(voting['_id']), username)

    return {"voting": voting, "voting_results": voting_results,
            'voting_percents': voting_percents, 'total': total,
            'your_vote': user_vote}


def _calculate_voting_percents(voting_results: dict, total: int):
    """
    Service function that calculates percentages for each voting option.
    Can't be accessed from the voting directly.
    :param voting_results: dict with per-option voting results
    :param total: total number of votes
    :return: dict with per-option vote percentages
    """
    return {
        option: int(round(voting_results[option] / total, 2) * 100)
        for option in voting_results
    }


def search_user_vote(voting_id, username):
    result = users.find_one({
        'username': username,
        f'votes.{voting_id}': {'$exists': True}
    },
        {
            f'votes.{voting_id}': 1,
            '_id': 0
        })
    if result:
        return result['votes'][voting_id]


def b64hash(string: str):
    """
    Service function that returns a b64 encoded string.
    :param string: string to encode
    :return: encoded string
    """
    return str(
        base64.b64encode(
            string.encode("utf-8")
        ),
        "utf-8"
    )
