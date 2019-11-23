from random import randint
from db_client import *
from db_setup import start
from copy import deepcopy

test_users = []

def gen_random_string():
    return "".join(
        [
            chr(randint(97, 97+22)) for i in range(10)
        ]
    )


def clean_all():
    votings.delete_many({})
    users.delete_many({})


def create_test_votes():
    q = "Do you drink vodka?"
    a = ["Yes", "No", "Maybe"]
    db_create_voting(q, a, 'admin')

    q = "Do you like pigeons?"
    a = ["Yes", "No", "Maybe"]
    db_create_voting(q, a, 'admin')


def create_test_users():
    for i in range(30):
        u, p = gen_random_string(), gen_random_string()
        db_create_user(u, p)
        test_users.append(u)


if __name__ == "__main__":
    # start()

    create_test_users()
    create_test_votes()
    assert test_users

    votings = db_list_votings()
    assert votings
    for tu in test_users:
        vote_for = randint(0, len(votings)-1)
        msg = db_vote(
            tu,
            votings[vote_for]['voting']['_id'],
            votings[vote_for]['voting']['options'][
                randint(0, len(votings[vote_for]['voting']['options'])-1)
            ]
        )

    print('\nInitial results...\n')

    dlv = db_list_votings()
    oldv = deepcopy(dlv[0])
    for i in dlv:
        print(i)

    print('\nChanging question...\n')

    db_update_voting(
        str(dlv[0]['voting']['_id']),
        'admin',
        question="Do you believe in love?"
    )

    dlv = db_list_votings()
    for i in dlv:
        print(i)

    print('\nChanging options...\n')

    db_update_voting(
        str(dlv[0]['voting']['_id']),
        'admin',
        options=["No", "Of course not"]
    )

    dlv = db_list_votings()
    for i in dlv:
        print(i)

    print('\nChanging both back...\n')

    db_update_voting(
        str(dlv[0]['voting']['_id']),
        'admin',
        question=oldv['voting']['question'],
        options=oldv['voting']['options']
    )

    dlv = db_list_votings()
    for i in dlv:
        print(i)
