from app import app, socket_
import unittest


class TestSocketIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connect(self):
        flask_test_client = app.test_client()
        client1 = socket_.test_client(
            app, namespace='/chat', flask_test_client=flask_test_client)
        client2 = socket_.test_client(
            app, namespace='/chat', flask_test_client=flask_test_client)
        self.assertTrue(client1.is_connected('/chat'))
        self.assertTrue(client2.is_connected('/chat'))
        self.assertNotEqual(client1.eio_sid, client2.eio_sid)
        r = client1.get_received('/chat')
        self.assertTrue(len(r) == 0)
        r = client2.get_received('/chat')
        self.assertTrue(len(r) == 0)

    def test_send_message_1(self):
        flask_test_client = app.test_client()
        client1 = socket_.test_client(
            app, namespace='/chat', flask_test_client=flask_test_client)
        self.assertTrue(client1.is_connected('/chat'))
        r = client1.get_received('/chat')
        self.assertTrue(len(r) == 0)
        client1.emit('send_message', {'data': 'test'}, namespace='/chat')
        r = client1.get_received('/chat')
        self.assertTrue(len(r) == 1)
        self.assertEqual(r[0]['name'], 'bot_response')
        self.assertIsInstance(r[0]['args'][0]['data'], str)

    def test_send_message_2(self):
        flask_test_client = app.test_client()
        client1 = socket_.test_client(
            app, namespace='/chat', flask_test_client=flask_test_client)
        client2 = socket_.test_client(
            app, namespace='/chat', flask_test_client=flask_test_client)
        self.assertTrue(client1.is_connected('/chat'))
        self.assertTrue(client2.is_connected('/chat'))
        r1 = client1.get_received('/chat')
        r2 = client2.get_received('/chat')
        self.assertTrue(len(r1) == 0)
        self.assertTrue(len(r2) == 0)
        client1.emit('send_message', {'data': 'test'}, namespace='/chat')
        client2.emit('send_message', {'data': 'test'}, namespace='/chat')
        r1 = client1.get_received('/chat')
        r2 = client2.get_received('/chat')
        self.assertTrue(len(r1) == 1)
        self.assertEqual(r1[0]['name'], 'bot_response')
        self.assertIsInstance(r1[0]['args'][0]['data'], str)
        self.assertTrue(len(r2) == 1)
        self.assertEqual(r2[0]['name'], 'bot_response')
        self.assertIsInstance(r2[0]['args'][0]['data'], str)

    def test_disconnect_request(self):
        flask_test_client = app.test_client()
        client1 = socket_.test_client(
            app, namespace='/chat', flask_test_client=flask_test_client)
        self.assertTrue(client1.is_connected('/chat'))
        r = client1.get_received('/chat')
        self.assertTrue(len(r) == 0)
        client1.emit('disconnect_request', namespace='/chat')
        r = client1.get_received('/chat')
        print(r)
        self.assertTrue(len(r) == 1)
        self.assertEqual(r[0]['name'], 'bot_response')
        self.assertIsInstance(r[0]['args'][0]['data'], str)


if __name__ == '__main__':
    unittest.main()
