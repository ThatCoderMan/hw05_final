from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='client')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_exists_at_desired_location(self):
        """Проверка доступности адресов приложения users"""
        test_urls = [
            reverse('users:login'),
            reverse('users:signup'),
            reverse('users:password_change'),
            reverse('users:password_change_done'),
            reverse('users:password_reset'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': '0', 'token': '0'}),
            reverse('users:password_reset_complete')
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
