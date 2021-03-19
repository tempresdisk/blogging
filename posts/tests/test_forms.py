import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.models import Comment, Post

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        )
        cls.post_another_author = Post.objects.create(
            text='Другой автор',
            author=get_user_model().objects.create_user(username='MC'),
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = self.test_post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """При отправке формы создаётся новая запись в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест',
            'image': self.uploaded,
        }
        self.authorized_client.post(reverse('new_post'), data=form_data)
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())

    def test_update_post(self):
        """
        При редактировании поста через форму изменяется соответствующая
        запись в базе данных.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редакция текста',
        }
        response = reverse('post_edit',
                           kwargs={'username': self.test_post.author.username,
                                   'post_id': self.test_post.id})
        test_id = self.test_post.id
        self.authorized_client.post(response, data=form_data)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(id=test_id).text, form_data['text'])

    def test_add_comment(self):
        """При отправке комментария создаётся новая запись в базе данных."""
        comment_count = Comment.objects.count()
        post = self.post_another_author
        author = post.author.username
        post_id = self.post_another_author.id
        reverse_name = reverse('add_comment',
                               kwargs={'username': author, 'post_id': post_id})
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(reverse_name, data=form_data)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(Comment.objects.get(post=post).text, form_data['text'])
