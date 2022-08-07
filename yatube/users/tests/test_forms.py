from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CreateFormTests(TestCase):
    def setUp(self):
        self.authorized_client = Client()

    def test_create_new_user(self):
        """Валидная форма создает нового пользователя."""
        users_count = User.objects.count()

        form_data = {
            'first_name': 'TestFirstName',
            'last_name': 'TestLastName',
            'username': 'username',
            'email': 'email@email.ru',
            'password1': 'TcHgQS9vgPwhr',
            'password2': 'TcHgQS9vgPwhr'
        }

        response = self.authorized_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        redirect_url = reverse('posts:index')
        self.assertRedirects(response, redirect_url)

        self.assertEqual(User.objects.count(), users_count + 1)

        self.assertTrue(
            User.objects.filter(
                first_name='TestFirstName',
                last_name='TestLastName',
                username='username',
                email='email@email.ru',
            ).exists()
        )
