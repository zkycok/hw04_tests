from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

from yatube.settings import POSTS_LIMIT

User = get_user_model()


class TaskPagesTests(TestCase):
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

        # запуталась, не совсем поняла
        # TODO
        # cls.index = ('posts/index.html', {'posts:index': cls.group.slug}, None)
        # cls.group_list = ('posts:group_list', {'posts/index.html': cls.group.slug}, {'slug': cls.group.slug})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_posts_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': self.user}),
            'posts/post_detail.html':
                (reverse('posts:post_detail',
                         kwargs={'post_id': self.post.id})),
            'posts/create_post.html':
                reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id}),
        }

        response = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first = response.context['page_obj'][0]

        self.assertEqual(first.text, self.post.text)
        self.assertEqual(first.author.id, self.user.id)
        self.assertEqual(first.group.title, self.group.title)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}))
        first = response.context['page_obj'][0]

        self.assertEqual(first.text, self.post.text)
        self.assertEqual(first.author.id, self.user.id)
        self.assertEqual(first.group.title, self.group.title)
        self.assertEqual(response.context['author'], self.user)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        first = response.context['page_obj'][0]
        self.assertEqual(first.text, self.post.text)
        self.assertEqual(first.author.id, self.user.id)
        self.assertEqual(first.group.title, self.group.title)
        self.assertEqual(response.context['group'], self.group)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].author, self.post.author)
        self.assertEqual(response.context['post'].group, self.post.group)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertTrue(response.context['is_edit'])
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context.get('form').instance, self.post)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertIsInstance(response.context['form'], PostForm)

    def test_no_post_in_right_pages(self):
        """Пост появляется на ожидаемых страница"""

        new_post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            id=3,
        )
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(new_post, index, 'поста нет на главной')
        self.assertIn(new_post, group, 'поста нет в профиле')
        self.assertIn(new_post, profile, 'поста нет в группе')

    def test_no_post_in_wrong_group(self):
        """Пост не попадает на страницу группы, к которой не принадлежит"""
        group_new = Group.objects.create(
            title='Новая группа',
            slug='other-group',
            description='Новая группа'
        )

        Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=group_new,
            id=2,
        )

        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group_new.slug}))
        first_object = response.context['page_obj'][0]
        self.assertNotIn(first_object.group.title, self.group.title)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.count_post = 10
        cls.create_post = 3
        cls.user = User.objects.create_user(username='Post_writer')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(POSTS_LIMIT + 3):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )
        cls.authorised_client = Client()
        cls.authorised_client.force_login(cls.user)
        cls.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for address in addresses:
            response = self.authorised_client.get(address)
            self.assertEqual(len(response.context['page_obj']), self.count_post)

    def test_second_page_contains_three_records(self):
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for address in addresses:
            response = self.authorised_client.get(address + '?page=2')
            self.assertEqual(len(response.context['page_obj']), self.create_post)
