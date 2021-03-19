from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location_guest(self):
        """
        Тест доступности URL анонимному пользователю:
        об авторе, о технологиях
        """
        urls_status_code = {
            '/': 200,
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for url, expected_status_code in urls_status_code.items():
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_status_code)

    def test_urls_use_correct_templates(self):
        """URL используют правильные шаблоны"""
        templates_url_names = {
            '/': 'index.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
