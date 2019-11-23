import requests
from random import randint
from db_client import db_delete_voting


AUTH = ('test_user', 'test_password')
TEST_QUESTION = 'Ein zwei Polizei?'
TEST_OPTIONS = ['Drei vier Grenadier', 'Funf sechs alte Kex', 'Sieben acht Gute Nacht']
SERVER_URL = 'http://127.0.0.1:5000/'
voting_id = None
my_vote_id = None


print('Showing votings w/o auth...')
resp = requests.get(
    f"{SERVER_URL}list-votings",
    auth=AUTH
)

print('Votings on server:')
for i in resp.json():
    print(i)
print('\n')

voting = resp.json()[0]['voting']
print(f'Will vote for: {voting["question"]}')


print('Creating a user...')
resp = requests.post(
    f"{SERVER_URL}create-user",
    json={
        'username': AUTH[0],
        'password': AUTH[1]
    }
)

print('Response:')
print(resp)
print(resp.text)
print('\n')


print('Creating a voting...')
resp = requests.post(
    f"{SERVER_URL}create-voting",
    json={
        'question': TEST_QUESTION,
        'options': TEST_OPTIONS
    },
    auth=AUTH
)

print('Response:')
print(resp)
print(resp.text)
print('\n')

my_vote_id = resp.text.split(" ")[3]


print(f'Voting in the new voting... I choose {TEST_OPTIONS[0]}')
resp = requests.post(
    f"{SERVER_URL}vote/{my_vote_id}",
    json={
        'option': TEST_OPTIONS[0]
    },
    auth=AUTH
)

print('Response:')
print(resp)
print(resp.text)
print('\n')


print('Getting votings...')
resp = requests.get(
    f"{SERVER_URL}list-votings",
    auth=AUTH
)

print('Votings on server:')
for i in resp.json():
    print(i)
print('\n')


print(f'Revoting... I choose {TEST_OPTIONS[1]}')
resp = requests.post(
    f"{SERVER_URL}vote/{my_vote_id}",
    json={
        'option': TEST_OPTIONS[1]
    },
    auth=AUTH
)

print('Response:')
print(resp)
print(resp.text)
print('\n')


print('Getting votings...')
resp = requests.get(
    f"{SERVER_URL}list-votings",
    auth=AUTH
)

print('Votings on server:')
for i in resp.json():
    print(i)
print('\n')




print(f'Just viewing a voting...')
resp = requests.get(
    f"{SERVER_URL}vote/{my_vote_id}",
    auth=AUTH
)


print('Response:')
print(resp)
print(resp.text)
print('\n')


print(f'Changing my voting... I replace {TEST_OPTIONS[1]} with \'Nichts\'')
TEST_OPTIONS.pop(1)
TEST_OPTIONS.append('Nichts')
resp = requests.post(
    f"{SERVER_URL}update-voting/{my_vote_id}",
    json={
        'question': '',
        'options': TEST_OPTIONS
    },
    auth=AUTH
)

print('Response:')
print(resp)
print(resp.text)
print('\n')


print('Response:')
print(resp)
print(resp.text)
print('\n')


print('Getting votings...')
resp = requests.get(
    f"{SERVER_URL}list-votings",
    auth=AUTH
)

print('Votings on server:')
for i in resp.json():
    print(i)
print('\n')



print(f'Just viewing a voting...')
resp = requests.get(
    f"{SERVER_URL}vote/{my_vote_id}",
    auth=AUTH
)

print('Response:')
print(resp)
print(resp.text)
print('\n')


print(f'Deleting my voting...')
resp = requests.get(
    f"{SERVER_URL}delete-voting/{my_vote_id}",
    auth=AUTH
)

print('Response:')
print(resp)
print(resp.text)
print('\n')


print('Getting votings...')
resp = requests.get(
    f"{SERVER_URL}list-votings"
)

print('Votings on server:')
for i in resp.json():
    print(i)
print('\n')
