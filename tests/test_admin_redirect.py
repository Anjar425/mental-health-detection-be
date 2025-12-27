import sys
import os
# Ensure project root is on PYTHONPATH so `import app` works when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.seeder import run_seeders

client = TestClient(app)


def test_admin_login_redirect_and_access():
    # Ensure seeders run so admin exists
    run_seeders()

    resp = client.post('/auth/login', json={'email': 'admin@example.com', 'password': 'admin123'})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get('redirect_to') == '/admin/dashboard'

    token = data.get('access_token')
    assert token

    headers = {'Authorization': f'Bearer {token}'}

    # Verify /auth/me returns redirect_to as well
    me = client.get('/auth/me', headers=headers)
    assert me.status_code == 200, me.text
    assert me.json().get('redirect_to') == '/admin/dashboard'

    r1 = client.get('/admin/rankings', headers=headers)
    assert r1.status_code == 200, r1.text

    r2 = client.get('/admin/consensus', headers=headers)
    assert r2.status_code == 200, r2.text