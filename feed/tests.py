from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .admin import NewsAdmin
from .models import CustomUser, News, Notification, UserNotificationSetting


class StucoNewsNotificationTests(TestCase):
    def setUp(self):
        self.publisher = CustomUser.objects.create_user(
            username="stuco_publisher",
            email="stuco_publisher@bjsmicschool.com",
            password="pw-Test-12345",
        )
        self.reader = CustomUser.objects.create_user(
            username="reader",
            email="reader@bjsmicschool.com",
            password="pw-Test-12345",
        )

    def publish_from_admin(self, title="Spirit week", body="Wear purple on Friday"):
        """Save a news item the way the Django admin does."""
        request = RequestFactory().post("/admin/feed/news/add/")
        request.user = self.publisher
        news = News(title=title, body=body)
        NewsAdmin(News, AdminSite()).save_model(request, news, form=None, change=False)
        return news

    def test_new_news_notifies_every_other_user(self):
        news = News.objects.create(title="Spirit week", body="Wear purple on Friday")

        notification = Notification.objects.get(recipient=self.reader, news=news)
        self.assertEqual(notification.notification_type, "stuco_news")
        self.assertIn("Spirit week", notification.message)
        self.assertFalse(notification.is_read)

    def test_publisher_is_not_notified(self):
        news = self.publish_from_admin()

        self.assertFalse(Notification.objects.filter(recipient=self.publisher).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.reader, news=news).exists())

    def test_admin_publish_records_the_publisher(self):
        news = self.publish_from_admin()

        notification = Notification.objects.get(recipient=self.reader, news=news)
        self.assertEqual(notification.actor, self.publisher)

    def test_news_without_publisher_has_no_actor(self):
        news = News.objects.create(title="Imported news", body="Body")

        notification = Notification.objects.get(recipient=self.reader, news=news)
        self.assertIsNone(notification.actor)

    def test_users_who_opted_out_are_skipped(self):
        setting = UserNotificationSetting.objects.create(user=self.reader)
        setting.notify_stuco_news = False
        setting.save()

        News.objects.create(title="Quiet news", body="Nothing to see")

        self.assertFalse(Notification.objects.filter(recipient=self.reader).exists())

    def test_editing_news_does_not_notify_again(self):
        news = News.objects.create(title="First version", body="Body")
        Notification.objects.all().delete()

        news.title = "Edited title"
        news.save()

        self.assertEqual(Notification.objects.count(), 0)

    def test_notifications_page_links_to_the_news_item(self):
        news = News.objects.create(title="Spirit week", body="Wear purple on Friday")
        self.client.force_login(self.reader)

        response = self.client.get(reverse("feed:notifications"))

        self.assertContains(response, "New StuCo news: Spirit week")
        self.assertContains(response, reverse("feed:news_post", args=[news.id]))


