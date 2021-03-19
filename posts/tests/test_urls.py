from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            id=1,
            title='Тестовое сообщество',
            slug='test-slug',
            description='Тестовое описание сообщества',
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=get_user_model().objects.create_user(username='DJ'),
            group=cls.test_group
        )
        cls.post_another_author = Post.objects.create(
            text='Тестовый текст',
            author=get_user_model().objects.create_user(username='MC')
        )
        author = cls.test_post.author.username
        another_author = cls.post_another_author.author.username
        cls.urls_auth_status_codes = {
            '/': 200,
            f'/group/{cls.test_group.slug}/': 200,
            '/new/': 200,
            f'/{cls.test_post.author.username}/': 200,
            f'/{cls.test_post.author.username}/{cls.test_post.id}/': 200,
            f'/{cls.test_post.author.username}/{cls.test_post.id}/edit/': 200,
            f'/{another_author}/{cls.post_another_author.id}/edit/': 302,
        }
        cls.urls_guest_status_codes = {
            '/': 200,
            f'/group/{cls.test_group.slug}/': 200,
            '/new/': 302,
            f'/{author}/': 200,
            f'/{author}/{cls.test_post.id}/edit/': 302,
            f'/{another_author}/{cls.post_another_author.id}/edit/': 302,
        }
        cls.templates_url_names = {
            '/': 'index.html',
            f'/group/{cls.test_group.slug}/': 'group.html',
            '/new/': 'new_post.html',
            f'/{author}/': 'profile.html',
            f'/{author}/{cls.test_post.id}/': 'post.html',
            f'/{author}/{cls.test_post.id}/edit/': 'new_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = self.test_post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exist_at_desired_location_auth(self):
        """Тест доступности страниц пользователю АВТОР/НЕ АВТОР"""
        urls_status_code = self.urls_auth_status_codes
        for reverse_name, expected_status_code in urls_status_code.items():
            with self.subTest(value=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, expected_status_code)

    def test_urls_exist_at_desired_location_guest(self):
        """Тест доступности страниц анонимному пользователю"""
        urls_status_code = self.urls_guest_status_codes
        for reverse_name, status_code in urls_status_code.items():
            with self.subTest(value=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)

    def test_url_redirects_anonymous_on_new_post(self):
        """Страница /new перенаправляет анонимного пользователя"""
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/new/'))

    def test_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = self.templates_url_names
        for reverse_name, template in templates_url_names.items():
            with self.subTest(value=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
