from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Текст для тестрирования 15 знаков текста',
            author=get_user_model().objects.create_user(username='тест')
        )

    def test_object_name_is_title_field(self):
        """В поле __str__  объекта post записано первые 15 знаков post.text"""
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Дайте волю графоманству',
            'group': 'Здесь можно выбрать сообщество для поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            id=1,
            title='тестирование Group',
            slug='test_group',
            description='описание сообщества',
        )
        cls.group = Group.objects.get(id=1)

    def test_object_name_is_title_field(self):
        """В поле __str__  объекта group записано название сообщества"""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
