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
        Post.objects.all().delete()
        post_count = Post.objects.count()

        templates_form_names = {'text': 'Самый новый пост',
                                'group': self.group.id,
                                }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=templates_form_names,
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        first_post = Post.objects.first()

        self.assertTrue(first_post.text, templates_form_names['text'])
        self.assertTrue(first_post.group, templates_form_names['group'])
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )

        group_new = Group.objects.create(
            title='Название новой группы',
            slug='test-slug-new',
            description='Описание новой группы'
        )

        templates_form_names = {'text': 'New post text',
                                'group': group_new.id}

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': post.id}),
            data=templates_form_names,
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.get(id=post.id)
        self.assertTrue(post.text, templates_form_names['text'])
        self.assertTrue(self.group.title, templates_form_names['group'])

    def test_not_auth(self):
        post_count = Post.objects.count()

        templates_form_names = {'text': 'Самый новый пост',
                                'group': self.group.id
                                }

        response_not_aut = self.guest_client.post(
            reverse('posts:post_create'),
            data=templates_form_names,
            follow=True)

        self.assertNotEqual(Post.objects.count(), post_count + 1)
