from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post


class TestView(TestCase):
    def setUp(self):
        self.client = Client()

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
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'frostbyte1231의 복습 노트')


        # has navbar
        self.navbar_test(soup)

        # 첨엔 게시물이 없는 상태 (다른 디비 쓰는 듯)
        self.assertEqual(Post.objects.count(), 0)

        main_area = soup.find('div', id='main-area')
        self.assertIn("No post yet", main_area.text)

        post_1 = Post.objects.create(
            title="first post",
            content="hello world"
        )
        post_2 = Post.objects.create(
            title='second_post',
            content='well'
        )
        self.assertEqual(Post.objects.count(), 2)

        # 포스트 목록 페이지 새로고침 (근데 이거 post_list 아닌가?)
        response = self.client.get("/blog/")
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)

        
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_1.title, main_area.text)
        self.assertIn(post_2.title, main_area.text)

        self.assertNotIn("No post yet", main_area.text)

    def test_post_detail(self):
        post_1 = Post.objects.create(
            title="first post",
            content="hello world"
        )
        self.assertEqual(post_1.get_absolute_url(), "/blog/1")

        response = self.client.get("/blog/1/")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)

        self.assertIn(post_1.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = soup.find('div', id='post-area')
        self.assertIn(post_1.title, post_area.text)
        # TODO: add author check
        self.assertIn(post_1.content, post_area.text)