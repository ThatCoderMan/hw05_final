from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
        )

    def test_post_object_name_is_text_fild(self):
        """Проверяем, что у модели корректно работает __str__."""
        post = ModelsTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_group_object_name_is_text_fild(self):
        """Проверяем, что у модели корректно работает __str__."""
        post = ModelsTest.group
        expected_object_name = post.title
        self.assertEqual(expected_object_name, str(post))

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = ModelsTest.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_help_text(self):
        """help_text в полях Post совпадает с ожидаемым."""
        post = ModelsTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
