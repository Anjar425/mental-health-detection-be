import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.seeder import run_seeders

client = TestClient(app)

try:
    run_seeders()
    resp = client.post('/auth/login', json={'email': 'admin@example.com', 'password': 'admin123'})
    print('login status', resp.status_code)
    print('response:', resp.json())
    if resp.status_code != 200:
        raise SystemExit('Login failed')
    data = resp.json()
    if data.get('redirect_to') != '/admin/dashboard':
        raise SystemExit(f"Unexpected redirect: {data.get('redirect_to')}")
    token = data.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    me = client.get('/auth/me', headers=headers)
    print('/auth/me', me.status_code, me.json())
    r1 = client.get('/admin/rankings', headers=headers)
    print('/admin/rankings', r1.status_code)
    r2 = client.get('/admin/consensus', headers=headers)
    print('/admin/consensus', r2.status_code)
    print('SMOKE OK')
except Exception as e:
    print('SMOKE FAIL:', str(e))
    raise