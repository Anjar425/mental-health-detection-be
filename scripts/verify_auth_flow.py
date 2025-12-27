from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print('Logging in as admin...')
resp = client.post('/auth/login', json={'email':'admin@example.com','password':'admin123'})
print('status', resp.status_code)
print(resp.json())
if resp.status_code != 200:
    raise SystemExit('Login failed')

data = resp.json()
assert 'role' in data and data['role'] == 'admin', 'Role is not admin in login response'

headers = {'Authorization': f"Bearer {data['access_token']}"}
me = client.get('/auth/me', headers=headers)
print('/auth/me', me.status_code, me.json())
assert me.status_code == 200 and me.json().get('role') == 'admin', '/auth/me did not return admin'

rank = client.get('/admin/rankings', headers=headers)
print('/admin/rankings', rank.status_code)
assert rank.status_code == 200, '/admin/rankings failed'

cons = client.get('/admin/consensus', headers=headers)
print('/admin/consensus', cons.status_code)
assert cons.status_code == 200, '/admin/consensus failed'

print('All auth flow checks passed')
