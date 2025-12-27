import requests

# Login first
login_response = requests.post('http://127.0.0.1:8000/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test group 2
rankings_resp = requests.get('http://127.0.0.1:8000/admin/groups/2/rankings', headers=headers)
print('Group 2 Rankings status:', rankings_resp.status_code)
if rankings_resp.status_code == 200:
    data = rankings_resp.json()
    print('Group:', data['group_name'])
    print('Rankings:')
    for ranking in data['rankings'][:3]:  # Show first 3
        print(f'  {ranking["rank"]}. {ranking["username"]} - Influence: {ranking["influence_percent"]}%')