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
            text='Тестовый пост для проверки',
            pub_date='Дата публикации',
            group=cls.group
        )

    def test_title_label_post(self):
        """Проверка заполнения атрибутов Post"""

        templates_field = {str(self.post): f'{self.post.text[:15]},'
                                           f' {self.post.pub_date},'
                                           f' {self.post.group}'}

        for field, value in templates_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)

    def test_title_label_group(self):
        """Проверка заполнения атрибутов Group"""

        templates_field = {str(self.group): f'Group: {self.group.slug}'}

        for field, value in templates_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
