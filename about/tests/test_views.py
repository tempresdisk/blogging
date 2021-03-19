from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_exist_at_desired_location_guest(self):
        """
        Тест доступности страниц анонимному пользователю:
        об авторе, о технологиях
        """
        urls_status_code = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
        }
        for reverse_name, expected_status_code in urls_status_code.items():
            with self.subTest(value=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, expected_status_code)

    def test_pages_use_correct_templates(self):
        """Статические страницы используют правильные шаблоны"""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(value=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
