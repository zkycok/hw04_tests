from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()

        templates_form_names = {'text': 'Самый новый пост',
                                'group': self.group.id,
                                'author': self.user}

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=templates_form_names,
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text=templates_form_names['text'],
            author=templates_form_names['author'],
            group=templates_form_names['group']
        ).exists())
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            id=1,
        )

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
        self.assertNotEqual(self.post, templates_form_names['text'])
        self.assertNotEqual(self.group, templates_form_names['group'])

    def test_not_auth(self):
        post_count = Post.objects.count()

        templates_form_names = {'text': 'Самый новый пост',
                                'group': self.group.id
                                }

        response_not_aut = self.guest_client.post(
            reverse('posts:post_create'),
            data=templates_form_names,
            follow=True)

        self.assertEqual(response_not_aut.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(), post_count + 1)

