from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_group',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_public_pages_exists_at_desired_location(self):
        """Проверка доступности адресов доступных всем пользователям."""
        test_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_group'}),
            reverse('posts:profile', kwargs={'username': 'author'}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            reverse('posts:post_create'),
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexustung_page_url_not_exists(self):
        """Проверка доступности адреса /unexustung_page/."""
        response = self.authorized_client.get('/unexustung_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
