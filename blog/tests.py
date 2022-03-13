from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_test1 = User.objects.create_user(username='test1', password='1234')
        self.user_test2 = User.objects.create_user(username='test2', password='1234')

        self.cat1 = Category.objects.create(name='cat1', slug='cat1')
        self.cat2 = Category.objects.create(name='cat2', slug='cat2')

        self.post_1 = Post.objects.create(
            title="first post",
            content="hello world",
            author=self.user_test1,
            category=self.cat1
        )
        self.post_2 = Post.objects.create(
            title='second_post',
            content='well',
            author=self.user_test2,
            category=self.cat2
        )
        self.post_3 = Post.objects.create(
            title='third_post',
            content='i am a post without category',
            author=self.user_test2
        )

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.cat1.name} ({self.cat1.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.cat2.name} ({self.cat2.post_set.count()})', categories_card.text)
        self.assertIn('NULL (1)', categories_card.text)
        

    def navbar_test(self, soup):
        # navbar는 리스트 / 디테일 페이지에 다 있음
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)


        logo_btn = navbar.find('a', text='frostbyte1231 blog')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')


    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(soup.title.text, 'frostbyte1231의 복습 노트')

        # has navbar
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertEqual(Post.objects.count(), 3)
        self.assertNotIn("No post yet", main_area.text)

        post_1_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_1.title, post_1_card.text)
        self.assertIn(self.post_1.category.name, post_1_card.text)

        
        post_2_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_2.title, post_2_card.text)
        self.assertIn(self.post_2.category.name, post_2_card.text)

        post_3_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_3.title, post_3_card.text)
        self.assertIn("No Category", post_3_card.text)

        self.assertIn(self.user_test1.username, main_area.text)
        self.assertIn(self.user_test2.username, main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get("/blog/")
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)

        
        main_area = soup.find('div', id='main-area')

        self.assertIn("No post yet", main_area.text)


    def test_post_detail(self):
        self.assertEqual(self.post_1.get_absolute_url(), "/blog/1")

        response = self.client.get("/blog/1/")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_1.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = soup.find('div', id='post-area')
        self.assertIn(self.post_1.title, post_area.text)
        self.assertIn(self.cat1.name, post_area.text)

        # TODO: add author check
        self.assertIn(self.post_1.content, post_area.text)
        self.assertIn(self.user_test1.username, post_area.text)
    
    def test_category_page(self):
        response = self.client.get(self.cat1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.cat1.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.cat1.name, main_area.text)
        self.assertIn(self.post_1.title, main_area.text)
        self.assertNotIn(self.post_2.title, main_area.text)
        self.assertNotIn(self.post_3.title, main_area.text)
