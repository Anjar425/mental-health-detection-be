import requests

# Login as user
login = requests.post('http://127.0.0.1:8000/auth/login', json={'email':'user1@example.com','password':'sandiAman123'})
print('Login status:', login.status_code)
if login.status_code != 200:
    print('Login failed:', login.text)
    exit(1)

data = login.json()
token = data['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('Logged in as user1')

# Get groups
groups_resp = requests.get('http://127.0.0.1:8000/admin/groups', headers=headers)
print('Groups status:', groups_resp.status_code)
if groups_resp.status_code == 200:
    groups = groups_resp.json()
    print('Groups:', [g['name'] for g in groups])
    if groups:
        group_id = groups[0]['id']
        group_name = groups[0]['name']
        print(f'Using group: {group_name} (id={group_id})')
    else:
        print('No groups available')
        exit(1)
else:
    print('Failed to get groups:', groups_resp.text)
    exit(1)

# Run DASS-21 with group_id
scores = [1,2,3,0,1,2,0,1,2,3,0,1,2,0,1,2,3,0,1,2,3]  # Sample scores
payload = {'scores': scores, 'type': '21', 'group_id': group_id}
qdss_resp = requests.post('http://127.0.0.1:8000/qdss', json=payload, headers=headers)
print('QDSS status:', qdss_resp.status_code)
if qdss_resp.status_code == 200:
    result = qdss_resp.json()
    print('QDSS result:', result)
else:
    print('QDSS failed:', qdss_resp.text)
    exit(1)

# Get history
history_resp = requests.get('http://127.0.0.1:8000/qdss/history', headers=headers)
print('History status:', history_resp.status_code)
if history_resp.status_code == 200:
    history = history_resp.json()
    print('History entries:', len(history))
    if history:
        latest = history[0]  # Most recent
        print('Latest history:', latest)
        if 'group_name' in latest:
            print(f'Group name in history: {latest["group_name"]}')
            if latest['group_name'] == group_name:
                print('SUCCESS: Group name matches!')
            else:
                print('ERROR: Group name does not match')
        else:
            print('ERROR: No group_name in history')
    else:
        print('No history entries')
else:
    print('History failed:', history_resp.text)