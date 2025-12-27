import requests

login = requests.post('http://127.0.0.1:8000/auth/login', json={'email':'admin@example.com','password':'admin123'})
print('login status', login.status_code)
print(login.text[:1000])
if login.status_code==200:
    data = login.json()
    redirect_to = data.get('redirect_to')
    print('redirect_to:', redirect_to)
    token = data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    r1 = requests.get('http://127.0.0.1:8000/admin/rankings', headers=headers)
    r2 = requests.get('http://127.0.0.1:8000/admin/consensus', headers=headers)
    print('\n--- /admin/rankings ---')
    print(r1.status_code)
    print(r1.text[:2000])
    print('\n--- /admin/consensus ---')
    print(r2.status_code)
    print(r2.text[:2000])
else:
    print('Login failed')
