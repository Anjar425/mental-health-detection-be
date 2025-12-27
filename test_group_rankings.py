import requests

# Login as admin
login = requests.post('http://127.0.0.1:8000/auth/login', json={'email':'admin@example.com','password':'admin123'})
print('Login status:', login.status_code)
if login.status_code != 200:
    print('Login failed:', login.text)
    exit(1)

data = login.json()
token = data['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('Logged in as admin')

# Get group rankings for group 1
rankings_resp = requests.get('http://127.0.0.1:8000/admin/groups/1/rankings', headers=headers)
print('Group Rankings status:', rankings_resp.status_code)
if rankings_resp.status_code == 200:
    rankings = rankings_resp.json()
    print('Group Rankings:')
    print(f'Group: {rankings["group_name"]} - {rankings["description"]}')
    print('Rankings:')
    for r in rankings['rankings']:
        print(f'  {r["rank"]}. {r["username"]} - Influence: {r["influence_percent"]}%')
    print('Consensus Matrix (first 3 items):')
    for c in rankings['consensus_matrix'][:3]:
        print(f'  Q{c["question_id"]}: D={c["depression"]}%, A={c["anxiety"]}%, S={c["stress"]}%')
else:
    print('Group Rankings failed:', rankings_resp.text)