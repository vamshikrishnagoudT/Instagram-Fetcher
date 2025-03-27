from django.test import TestCase
from .services import InstagramService, SummarizationService, XService
from unittest.mock import patch

class InstagramFetcherTests(TestCase):
    def test_instagram_fetch(self):
        """Test Instagram data retrieval (simulated)."""
        service = InstagramService()
        data = service.fetch_latest_post()
        self.assertIsNotNone(data)
        self.assertIn("caption", data)
        self.assertIn("image_url", data)
        self.assertEqual(data["caption"], "Simulated BBC News post: Breaking news update.")

    def test_summarization(self):
        """Test caption summarization."""
        service = SummarizationService()
        caption = "This is a long caption about a breaking news event that needs summarizing."
        summary = service.summarize_caption(caption)
        self.assertTrue(len(summary) <= 280)
        self.assertNotEqual(summary, caption)
        self.assertTrue(len(summary) < len(caption))

    @patch('tweepy.Client.create_tweet')
    def test_tweet_posting(self, mock_create_tweet):
        """Test tweet posting (mocked real API)."""
        mock_create_tweet.return_value = None  # Pretend it worked
        service = XService()
        text = "Breaking news summary."
        result = service.post_tweet(text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tweet"], text)
        mock_create_tweet.assert_called_once_with(text=text)

    def test_username_change(self):
        """Test changing Instagram username."""
        service = InstagramService()
        service.set_username("cnn")
        self.assertEqual(service.username, "cnn")
        self.assertEqual(service.base_url, "https://www.instagram.com/cnn/")