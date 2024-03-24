import unittest
from project2 import app as project2
import unittest
import json
import os


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = project2.test_client()

    def test_connect(self):
        response = self.app.get('/') #test if server is connected
        self.assertEqual(response.status_code, 200)

    def test_auth(self):
        response = self.app.post('/auth') #test if /auth is working
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_auth_expired(self):
        response = self.app.post('/auth?expired=true') #test of the expiration
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_jwks(self):
        response = self.app.get('/.well-known/jwks.json') #test for jwks
        self.assertEqual(response.status_code, 200)
        jwks = json.loads(response.data)

    def database_test(self):
        return os.path.exists(self)
    
    if database_test('totally_not_my_privateKeys.db'):
        print('200. Success')
    else:
        print('Error')

    

if __name__ == '__main__':
    unittest.main()
