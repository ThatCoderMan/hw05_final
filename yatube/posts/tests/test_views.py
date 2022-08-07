import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()

TЕMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TЕMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_image = SimpleUploadedFile(
            name='image.gif',
            content=image,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='test_profile')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_group',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='test post',
            image=uploaded_image
        )

        cls.second_user = User.objects.create_user(
            username='second_test_profile')
        cls.second_group = Group.objects.create(
            title='second test group',
            slug='second_test_group',
            description='second_test_description',
        )
        cls.second_post = Post.objects.create(
            author=cls.second_user,
            group=cls.second_group,
            text='second test post'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TЕMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.second_user)
        self.guest_client = Client()
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адреса использует соответствующие шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_group'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test_profile'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            '/notexist/': 'core/404.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        title = response.context['title']
        page_obj = response.context['page_obj']
        self.assertEqual(title, 'Последние обновления на сайте')
        self.assertIn(self.post, page_obj)
        self.assertIsNotNone(page_obj[self.post.pk].image)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        url = reverse('posts:group_list', kwargs={'slug': 'test_group'})
        response = self.authorized_client.get(url)
        title = response.context['title']
        group = response.context['group']
        page_obj = response.context['page_obj']
        self.assertEqual(title, 'Записи сообщества test group')
        self.assertEqual(group, self.group)
        self.assertEqual(page_obj[0], self.post)
        self.assertIsNotNone(page_obj[0].image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        url = reverse('posts:profile', kwargs={'username': 'test_profile'})
        response = self.authorized_client.get(url)
        title = response.context['title']
        author = response.context['author']
        page_obj = response.context['page_obj']
        following = response.context['following']
        self.assertEqual(title, 'Профайл пользователя test_profile')
        self.assertEqual(author, self.user)
        self.assertEqual(page_obj[0], self.post)
        self.assertIsNotNone(page_obj[0].image)
        self.assertFalse(following)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(url)
        title = response.context['title']
        post = response.context['post']
        self.assertEqual(title, 'Пост test post')
        self.assertEqual(post, self.post)
        self.assertIsNotNone(post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        url = reverse('posts:post_create')
        response = self.authorized_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон PostEdit сформирован с правильным контекстом."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_in_right_pages(self):
        """Новый пост появляется на нужных страницах"""
        test_urls = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': 'second_test_group'}),
            reverse('posts:profile',
                    kwargs={'username': 'second_test_profile'})
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                print(response.context)
                page_obj = response.context['page_obj']
                self.assertIn(self.second_post, page_obj)

    def test_new_post_not_in_another_pages(self):
        """Новый пост не появляется на других страницах"""
        test_urls = [
            reverse('posts:group_list',
                    kwargs={'slug': 'test_group'}),
            reverse('posts:profile',
                    kwargs={'username': 'test_profile'})
        ]
        for url in test_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                page_obj = response.context['page_obj']
                self.assertNotIn(self.second_post, page_obj)

    def test_posts_edit_url_redirect_not_author_on_post_page(self):
        """Страница по адресу /posts/1/edit/ перенаправит не автора
        на страницу поста."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        url_redirect = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.pk})
        response = self.authorized_not_author_client.get(url, follow=True)
        self.assertRedirects(response, url_redirect)

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/1/edit/ перенаправит анонимного
        пользователя на страницу поста."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        url_redirect = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.pk})
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, url_redirect)

    def test_create_url_reditect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_no_comment_access_for_guest_client(self):
        """Комментирование не доступно для неавторизованных пользователей"""
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_comment_added_to_post_detail_page(self):
        """Комментарий добавляется на страницу просмотра поста"""
        comment = Comment(
            post=self.post,
            author=self.user,
            text='test comment'
        )
        comment.save()
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(url)
        comments = response.context['comments']
        self.assertEqual(comments[0], comment)

    def test_index_page_cache(self):
        """Главная страница использует кеширование"""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        post_for_del = Post.objects.create(
            author=self.user,
            text='post_for_del',
        )
        cache.clear()
        response_cached = self.authorized_client.get(reverse('posts:index'))
        post_for_del.delete()
        posts_cached = response_cached.content
        self.assertNotEqual(posts, posts_cached)

        cache.clear()
        response_cleared = self.authorized_client.get(reverse('posts:index'))
        posts_cleared = response_cleared.content
        self.assertEqual(posts, posts_cleared)

    def test_follow_page_show_current_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        Follow(
            user=self.second_user,
            author=self.user
        ).save()
        url = reverse('posts:follow_index')
        response = self.authorized_not_author_client.get(url)
        page_obj = response.context['page_obj']
        self.assertIn(self.post, page_obj)
        self.assertNotIn(self.second_post, page_obj)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_profile')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_group',
            description='test_description',
        )
        for post_id in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'test post {post_id}'
            )
        cls.test_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_group'}),
            reverse('posts:profile', kwargs={'username': 'test_profile'})
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        for url in self.test_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        for url in self.test_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
