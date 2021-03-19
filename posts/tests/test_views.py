import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.test_group = Group.objects.create(
            title='Тестовое сообщество',
            slug='test-slug',
            description='Тестовое описание сообщества',
        )
        cls.test_group_empty = Group.objects.create(
            title='Пустое сообщество',
            slug='empty',
            description='Для ловли багов',
        )
        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=get_user_model().objects.create_user(username='DJ'),
            group=cls.test_group,
            image=cls.uploaded,
        )
        cls.post_another_author = Post.objects.create(
            text='Другой автор',
            author=get_user_model().objects.create_user(username='MC'),
            group=cls.test_group
        )
        args_post = [cls.test_post.author.username, cls.test_post.id]
        post_URL = reverse('post', args=args_post)
        post_edit_URL = reverse('post_edit', args=args_post)
        username = cls.test_post.author.username
        cls.templates_reverse_names = {
            reverse('index'): 'index.html',
            reverse('group', args=[cls.test_group.slug]): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse('profile', kwargs={'username': username}): 'profile.html',
            post_URL: 'post.html',
            post_edit_URL: 'new_post.html',
            reverse('follow_index'): 'follow.html',
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        posts = []
        for i in range(1, 12):
            posts.append(Post(
                text='Paginator' + str(i),
                author=cls.test_post.author,
                group=cls.test_group
            ))
        Post.objects.bulk_create(posts)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = self.test_post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """Страницы используют соответствующий шаблон."""
        templates_reverse_names = self.templates_reverse_names
        for reverse_name, template in templates_reverse_names.items():
            with self.subTest(value=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_index_shows_correct_context(self):
        """
        Шаблон index сформирован с правильным контекстом.
        Пост для сообщества test-slug отображается на главной странице.
        Паджинатор для этой страницы работает согласно ожиданиям.
        """
        response_1p = self.guest_client.get(reverse('index') + '?page=1')
        page = response_1p.context['page']
        self.assertEqual(len(page), 10)
        self.assertEqual(page[0].group.title, self.test_group.title)
        response_2p = self.guest_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response_2p.context['page']), 3)

    def test_page_group_shows_correct_context(self):
        """
        Шаблон group/test-slug сформирован с правильным контекстом.
        Пост для сообщества test-slug отображается только в этом сообществе.
        Паджинатор для этой страницы работает согласно ожиданиям.
        """
        rev_page = reverse('group', kwargs={'slug': 'test-slug'})
        reverse_empty_group = reverse('group', kwargs={'slug': 'empty'})
        response_group_title = self.guest_client.get(rev_page + '?page=1')
        self.assertEqual(response_group_title.context['group'],
                         self.test_group)
        response_empty_group = self.guest_client.get(reverse_empty_group)
        self.assertEqual(len(response_empty_group.context['page']), 0)
        response_paginator_1p = self.guest_client.get(rev_page + '?page=1')
        self.assertEqual(len(response_paginator_1p.context['page']), 10)
        response_paginator_2p = self.guest_client.get(rev_page + '?page=2')
        posts = self.guest_client.get(rev_page).context['group'].posts.all()
        self.assertIn(self.test_post, posts)
        self.assertEqual(len(response_paginator_2p.context['page']), 3)

    def test_page_new_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = self.form_fields
        self.assertEqual(response.context['is_edit'], False)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_post_edit_shows_correct_context(self):
        """Шаблон страницы post_edit сформирован с правильным контекстом."""
        kwargs = {'username': self.user.username, 'post_id': self.test_post.id}
        post_edit_url = reverse('post_edit', kwargs=kwargs)
        response = self.authorized_client.get(post_edit_url)
        form_fields = self.form_fields
        self.assertEqual(response.context['is_edit'], True)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_profile_shows_correct_context(self):
        """Шаблон страницы profile сформирован с правильным контекстом.
           Паджинатор для этой страницы работает согласно ожиданиям.
        """
        username = self.user.username
        reverse_name = reverse('profile', kwargs={'username': username})
        response_1p = self.guest_client.get(reverse_name + '?page=1')
        context_1p = response_1p.context
        self.assertEqual(len(context_1p['page']), 10)
        self.assertEqual(context_1p['page'][0].author.username, username)
        response_2p = self.guest_client.get(reverse_name + '?page=2')
        self.assertEqual(len(response_2p.context['page']), 2)

    def test_page_post_shows_correct_context(self):
        """Шаблон страницы post сформирован с правильным контекстом.
        """
        kwargs = {'username': self.user.username, 'post_id': self.test_post.id}
        post_URL = reverse('post', kwargs=kwargs)
        response = self.guest_client.get(post_URL)
        context = response.context
        expected_post = self.test_post
        expected_post_count = Post.objects.filter(
                                        author=expected_post.author).count()
        self.assertEqual(context['post'], expected_post)
        self.assertEqual(context['post_count'], expected_post_count)

    def test_error_pages_use_correct_template(self):
        """Страницы ошибок используют соответствующий шаблон."""
        templates_reverse_names = {
            reverse('404'): 'misc/404.html',
            reverse('500'): 'misc/500.html',
        }
        for reverse_name, template in templates_reverse_names.items():
            with self.subTest(value=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_error_pages_show_correct_context(self):
        """Шаблоны страниц ошибок сформированы
           с правильным контекстом и статусом.
        """
        response_500 = self.guest_client.get(reverse('500'))
        response_404 = self.guest_client.get(reverse('404'))
        expected_context_404 = reverse('404')
        self.assertEqual(response_404.status_code, 404)
        self.assertEqual(response_500.status_code, 500)
        self.assertEqual(response_404.context['path'], expected_context_404)

    def test_index_page_cache(self):
        """Кэш главной страницы работает корректно"""
        response_1 = self.guest_client.get(reverse('index'))
        Post.objects.create(text='test_cache', author=self.user)
        response_2 = self.guest_client.get(reverse('index'))
        self.assertHTMLEqual(str(response_1.content), str(response_2.content))
        cache.clear()
        response_3 = self.guest_client.get(reverse('index'))
        self.assertHTMLNotEqual(str(response_1.content), str(response_3.content))

    def test_follow_unfollow(self):
        """Авторизованный пользователь может подписываться на других
           пользователей и удалять их из подписок."""
        author = self.post_another_author.author
        author_not_user = {'username': author.username}
        author_is_user = {'username': self.user.username}

        reverse_follow = reverse('profile_follow', kwargs=author_not_user)
        self.authorized_client.get(reverse_follow)
        self.assertTrue(Follow.objects.filter(author=author).exists())

        reverse_follow_error = reverse('profile_follow', kwargs=author_is_user)
        self.authorized_client.get(reverse_follow_error)
        self.assertFalse(Follow.objects.filter(author=self.user).exists())

        reverse_unfollow = reverse('profile_unfollow', kwargs=author_not_user)
        self.authorized_client.get(reverse_unfollow)
        self.assertFalse(Follow.objects.filter(author=author).exists())

    def test_page_follow_yes_following(self):
        """Новая запись пользователя появляется в ленте подписавшихся."""
        kwargs = {'username': self.post_another_author.author.username}
        profile_follow_URL = reverse('profile_follow', kwargs=kwargs)
        self.authorized_client.get(profile_follow_URL)
        response = self.authorized_client.get(reverse('follow_index'))
        context = response.context['page']
        self.assertIn(self.post_another_author, context)

    def test_page_follow_no_following(self):
        """Новая запись пользователя НЕ появляется в ленте неподписавшихся."""
        response = self.authorized_client.get(reverse('follow_index'))
        context = response.context['page']
        self.assertNotIn(self.post_another_author, context)

    def test_comment(self):
        """Только авторизированный пользователь может комментировать посты."""
        comment_count = Comment.objects.count()
        author = self.post_another_author.author.username
        post_id = self.post_another_author.id
        kwargs = {'username': author, 'post_id': post_id}
        reverse_name = reverse('add_comment', kwargs=kwargs)
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(reverse_name, data=form_data)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.guest_client.post(reverse_name, data=form_data)
        self.assertNotEqual(Comment.objects.count(), comment_count + 2)
