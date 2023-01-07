from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):
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
            group=cls.group,
            id=1,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()

        templates_form_names = {'text': self.post.text,
                                'group': self.group.id}

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=templates_form_names,
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text=self.post.text,
            author=self.post.author,
            group=self.group.id
        ).exists())
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        self.group_new = Group.objects.create(
            title="Название новой группы",
            slug="test-slug-new",
            description="Описание новой группы"
        )

        templates_form_names = {'text': 'New post text',
                                'group': self.group_new.id}

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=templates_form_names,
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            pub_date=self.post.pub_date,
            author=self.post.author,
            group=self.group_new.id
        ).exists())
        self.assertNotEqual(self.post, templates_form_names.get('text'))
        self.assertNotEqual(self.group, templates_form_names.get('group'))
