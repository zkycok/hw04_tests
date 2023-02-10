from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки'[:15],
            pub_date='Дата публикации',
            group=cls.group
        )

    def test_title_label_post(self):
        """Проверка заполнения атрибутов Post"""

        templates_field = {self.post.text: self.post.text[:15],
                           self.post.pub_date: self.post.pub_date,
                           self.group: self.group,
                           self.user: self.user}

        for field, value in templates_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)

    def test_title_label_group(self):
        """Проверка заполнения атрибутов Group"""

        templates_field = {self.group.title: 'Тестовая группа',
                           self.group.slug: 'Тестовый слаг',
                           self.group.description: 'Тестовое описание'}

        for field, value in templates_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
