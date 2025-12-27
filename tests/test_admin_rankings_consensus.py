import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.seeder import run_seeders

client = TestClient(app)


def get_token(email, password):
    resp = client.post('/auth/login', json={'email': email, 'password': password})
    assert resp.status_code == 200, resp.text
    return resp.json()['access_token']


def test_admin_endpoints_require_auth_and_role():
    run_seeders()

    # Unauthenticated should be 401
    r = client.get('/admin/rankings')
    assert r.status_code == 401

    # Authenticated but not admin (expert) -> 403
    expert_token = get_token('expert1@example.com', 'sandiAman123')
    r = client.get('/admin/rankings', headers={'Authorization': f'Bearer {expert_token}'})
    assert r.status_code == 403

    # Admin can access
    admin_token = get_token('admin@example.com', 'admin123')
    r = client.get('/admin/rankings', headers={'Authorization': f'Bearer {admin_token}'})
    assert r.status_code == 200

    r2 = client.get('/admin/consensus', headers={'Authorization': f'Bearer {admin_token}'})
    assert r2.status_code == 200


def test_rankings_include_only_experts_and_ordering():
    run_seeders()
    admin_token = get_token('admin@example.com', 'admin123')
    r = client.get('/admin/rankings', headers={'Authorization': f'Bearer {admin_token}'})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

    # Expect only experts (seeded experts are expert1..expert4)
    usernames = [x['username'] for x in data]
    assert all(u.startswith('expert') for u in usernames)
    assert 'admin' not in usernames
    assert 'user1' not in usernames

    # Check weights are sorted descending
    weights = [x['weight'] for x in data]
    assert weights == sorted(weights, reverse=True)

    # Check rank is dense and starts at 1
    ranks = [x['rank'] for x in data]
    assert ranks[0] == 1
    # ranks set should be consecutive integers starting at 1
    unique_ranks = sorted(set(ranks))
    assert unique_ranks == list(range(1, len(unique_ranks) + 1))


def test_consensus_schema_and_values():
    run_seeders()
    admin_token = get_token('admin@example.com', 'admin123')
    r = client.get('/admin/consensus', headers={'Authorization': f'Bearer {admin_token}'})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 21

    ids = [item['dass21_id'] for item in data]
    assert ids == list(range(1, 22))

    # Each item should have numeric percentages
    for item in data:
        assert isinstance(item['depression'], (int, float))
        assert isinstance(item['anxiety'], (int, float))
        assert isinstance(item['stress'], (int, float))
        # Basic sanity: values between 0..100
        assert 0.0 <= item['depression'] <= 100.0
        assert 0.0 <= item['anxiety'] <= 100.0
        assert 0.0 <= item['stress'] <= 100.0