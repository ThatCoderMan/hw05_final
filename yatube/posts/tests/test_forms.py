import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()

TЕMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TЕMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        )
        cls.form = PostForm()

        cls.follower_user = User.objects.create_user(
            username='follower_user')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TЕMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower_user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

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
        form_data = {
            'text': 'test post 2',
            'group': self.group.pk,
            'image': uploaded_image
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        redirect_url = reverse('posts:profile',
                               kwargs={'username': 'test_profile'})
        self.assertRedirects(response, redirect_url)

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text='test post 2',
                author=self.user,
                group=self.group,
                image='posts/image.gif'
            ).exists()
        )

    def test_edit_psot(self):
        """Валидная форма редактирования записи в Post."""
        Post.objects.create(
            author=self.user,
            group=self.group,
            text='test post'
        )

        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_image = SimpleUploadedFile(
            name='image_edited.gif',
            content=image,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test post 1 edited',
            'group': self.group.pk,
            'image': uploaded_image
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.group.pk}),
            data=form_data,
            follow=True
        )

        redirect_url = reverse('posts:post_detail',
                               kwargs={'post_id': self.group.pk})
        self.assertRedirects(response, redirect_url)

        self.assertTrue(
            Post.objects.filter(
                text='test post 1 edited',
                author=self.user,
                group=self.group,
                image='posts/image_edited.gif'
            ).exists()
        )

    def test_add_comment(self):
        """Валидная форма добпаления комментария к посту."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'test comment',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        redirect_url = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.pk})
        self.assertRedirects(response, redirect_url)

        self.assertEqual(Comment.objects.count(), comments_count + 1)

        self.assertTrue(
            Comment.objects.filter(
                text='test comment',
                post=self.post,
                author=self.user,
            ).exists()
        )

    def test_follow(self):
        """Валидная форма подписки на пользователя."""
        follow_count = Follow.objects.count()

        response = self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}),
            follow=True
        )
        redirect_url = reverse('posts:profile',
                               kwargs={'username': self.user.username})
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower_user,
                author=self.user
            ).exists()
        )

    def test_unfollow(self):
        """Валидная форма отписки от пользователя."""
        Follow(
            user=self.follower_user,
            author=self.user
        ).save()

        follow_count = Follow.objects.count()

        response = self.follower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username}),
            follow=True
        )
        redirect_url = reverse('posts:profile',
                               kwargs={'username': self.user.username})
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower_user,
                author=self.user
            ).exists()
        )
