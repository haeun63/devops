import unittest
import app as guestbook


class GuestbookTest(unittest.TestCase):
    def setUp(self):
        guestbook.app.config.update(TESTING=True)
        guestbook._memory_entries.clear()
        self.client = guestbook.app.test_client()

    def test_health(self):
        response = self.client.get('/healthz')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    def test_add_and_read(self):
        response = self.client.post(
            '/add',
            data={
                'name': 'student',
                'message': 'hello'
            }
        )
        self.assertEqual(response.status_code, 302)

        entries = self.client.get('/api/entries').get_json()
        self.assertEqual(entries['count'], 1)
        self.assertEqual(entries['entries'][0]['message'], 'hello')

