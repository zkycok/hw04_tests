from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username="auth")

        cls.group = Group.objects.create(
            title="Название группы",
            slug="test-slug",
            description="Описание группы"
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

        name_create = 'posts/create_post.html'
        cls.templates_url_names_public = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{cls.group.slug}/',
            'posts/profile.html': f'/profile/{cls.user.username}/',
            'posts/post_detail.html': f'/posts/{cls.post.id}/',
        }

        cls.templates_url_names_private = {
            'posts/create_post.html': f'/posts/{cls.post.id}/edit/',
            name_create: '/create/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_author_users(self):
        """Доступность всех страниц для
         авторизованного пользователя-автора тестового поста"""
        templates_url_names = (
            self.templates_url_names_public
            | self.templates_url_names_private)

        for address in templates_url_names.values():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_urls_not_author_users(self):
        """Доступность публичных страниц для неавторизованного пользователя"""

        for address in self.templates_url_names_public.values():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_urls_not_author_users_redirect(self):
        """Редирект неавторизованного с публичных страниц"""

        for address in self.templates_url_names_private.values():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 302)

    def test_urls_not_author_users_edit_redirect(self):
        """Редирект авторизованного при попытке редактирования чужого поста"""

        user_new = User.objects.create_user(username="auth_new")

        post_new = Post.objects.create(
            text='Тестовый текст новый',
            author=user_new,
        )

        response = self.authorized_client.get(f'/posts/{post_new.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = (
            self.templates_url_names_public
            | self.templates_url_names_private)

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_wrong_uri_returns_404(self):
        response = self.authorized_client.get('/something/really/weird/')
        self.assertEqual(response.status_code, 404)
