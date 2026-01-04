import requests

base = 'http://127.0.0.1:8000'

# Login as admin
r = requests.post(base + '/auth/login', json={'email':'admin@example.com','password':'admin123'})
print('login status', r.status_code)
if r.status_code != 200:
    print(r.text)
    raise SystemExit(1)

token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# Fetch group 1 rankings
resp = requests.get(base + '/admin/groups/1/rankings', headers=headers)
print('rankings status', resp.status_code)
print(resp.text)
