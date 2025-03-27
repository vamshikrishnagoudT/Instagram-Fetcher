import requests
from bs4 import BeautifulSoup
import logging
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import pipeline
import tweepy
from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Part 1: Instagram Service
class InstagramService:
    def __init__(self, username="bbcnews"):
        self.username = username
        self.base_url = f"https://www.instagram.com/{username}/"

    def fetch_latest_post_with_requests(self):

        try:
            response = requests.get(self.base_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', text=re.compile('window._sharedData'))
            if not script_tag:
                logger.error("No shared data script found with requests")
                return None
            json_str = script_tag.text.split(' = ', 1)[1].rstrip(';')
            data = json.loads(json_str)
            edges = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
            if not edges:
                logger.error("No posts found in shared data")
                return None
            latest_post = edges[0]['node']
            caption = latest_post['edge_media_to_caption']['edges'][0]['node']['text'] if latest_post['edge_media_to_caption']['edges'] else "No caption"
            image_url = latest_post['display_url']
            logger.info(f"Fetched post with requests: {caption[:50]}...")
            return {"caption": caption, "image_url": image_url}
        except Exception as e:
            logger.error(f"Requests method failed: {str(e)}")
            return None

    def fetch_latest_post_with_selenium(self):

        """Fallback to Selenium for dynamic content."""

        driver = None
        try:
            options = Options()
            options.add_argument("--headless")

            options.add_argument("--no-sandbox")  # Fix for some environments
            options.add_argument("--disable-dev-shm-usage")  # Avoid resource issues

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            service = Service(executable_path="/usr/bin/chromedriver")
            logger.info("Starting ChromeDriver...")
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("ChromeDriver started successfully!")

            logger.info(f"Loading {self.base_url} with Selenium...")
            driver.get(self.base_url)
            logger.info("Waiting for page to load...")

            # Wait for body or a more generic element

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            logger.info("Page loaded, parsing source...")
            page_source = driver.page_source
            logger.info(f"Page source snippet: {page_source[:200]}")
            soup = BeautifulSoup(page_source, 'html.parser')
            script_tag = soup.find('script', text=re.compile('window._sharedData'))
            if not script_tag:
                logger.error("No shared data script found with Selenium")
                if "login" in page_source.lower():
                    logger.error("Likely hit login page; scraping blocked")
                driver.quit()
                return None

            json_str = script_tag.text.split(' = ', 1)[1].rstrip(';')
            data = json.loads(json_str)
            edges = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
            if not edges:
                logger.error("No posts found with Selenium")
                driver.quit()
                return None

            latest_post = edges[0]['node']
            caption = latest_post['edge_media_to_caption']['edges'][0]['node']['text'] if latest_post['edge_media_to_caption']['edges'] else "No caption"
            image_url = latest_post['display_url']
            logger.info(f"Fetched post with Selenium: {caption[:50]}...")
            driver.quit()
            return {"caption": caption, "image_url": image_url}

        except Exception as e:
            logger.error(f"Selenium method failed: {str(e)}")
            if driver:
                driver.quit()
            return None
    def fetch_latest_post(self):
        post_data = self.fetch_latest_post_with_requests()
        if post_data:
            return post_data
        logger.info("Falling back to Selenium...")
        post_data = self.fetch_latest_post_with_selenium()
        if post_data:
            return post_data
        logger.warning("Scraping failed; returning simulated data")
        return {
            "caption": "Tech News: Apple announces the iPhone 16 with groundbreaking AI features! What do you think.",
            "image_url": "https://fakeimage.com/iphone16.jpg"
        }

    def set_username(self, new_username):
        self.username = new_username
        self.base_url = f"https://www.instagram.com/{new_username}/"
        logger.info(f"Username changed to {new_username}")

# Part 2: Summarization Service
class SummarizationService:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_caption(self, caption, max_length=280):
        """Summarizes caption to fit within 280 characters and be shorter than input."""
        try:
            summary = self.summarizer(caption, max_length=8, min_length=3, do_sample=False)[0]['summary_text']
            target_length = min(max_length, max(10, len(caption) // 2))

            if len(summary) > target_length or "CNN.co.uk" in summary:  # Avoid weird CNN output
                summary = "Breaking news..."  # Force a sensible default if BART messes up

            if len(summary) > target_length or "CNN.co.uk" in summary:
                summary = "Breaking news..."

            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            logger.info(f"Summarized to: {summary} ({len(summary)} chars)")
            return summary
        except Exception as e:
            logger.error(f"Summary failed: {e}")

            return "Breaking news..."  # Better fallback
# Part 2: X Service
class XService:
    def __init__(self):
        self.simulate = True  # Set to False with real credentials
        # Uncomment and configure with real X API keys if available:
        # auth = tweepy.OAuthHandler("consumer_key", "consumer_secret")
        # auth.set_access_token("access_token", "access_token_secret")
        # self.api = tweepy.API(auth)

    def post_tweet(self, text):
        """Posts a tweet or simulates it."""
        try:
            if self.simulate:
                logger.info(f"Simulated tweet posted: {text}")
                return {"status": "success", "tweet": text}
            # self.api.update_status(text)  # Uncomment for real posting
            # logger.info(f"Tweet posted: {text}")
            # return {"status": "success", "tweet": text}
        except Exception as e:

            return "Breaking news..."

# Part 2: X Service
class XService:
    def __init__(self):
        consumer_key = "kDt5GDF4k6hkVmbBWVLUlV9az"  # Your real key here
        consumer_secret = "mZeTkJcSdAY0JnaukU2UNtUtAUQ3gvsYBrPsdEwkhgLxZexYH2"  # Your real key here
        access_token = "1448607383190601731-HDSgfZwLRzN6ER2Vf50U5XYNR5CFXu"  # Your real key here
        access_token_secret = "NaDDSeYqwyXaokhq3OhNVLeVG8lnIgN3WogGNu4NaZSaS"  # Your real key here
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        try:
            self.api.verify_credentials()
            logger.info("X.com API authentication successful")
        except Exception as e:
            logger.error(f"X.com API authentication failed: {e}")
            raise

    def post_tweet(self, text):
        try:
            client = tweepy.Client(
                consumer_key="kDt5GDF4k6hkVmbBWVLUlV9az",  # Your real key here
                consumer_secret="mZeTkJcSdAY0JnaukU2UNtUtAUQ3gvsYBrPsdEwkhgLxZexYH2",  # Your real key here
                access_token="1448607383190601731-HDSgfZwLRzN6ER2Vf50U5XYNR5CFXu",  # Your real key here
                access_token_secret="NaDDSeYqwyXaokhq3OhNVLeVG8lnIgN3WogGNu4NaZSaS"  # Your real key here
            )
            client.create_tweet(text=text)
            logger.info(f"Tweet posted: {text}")
            return {"status": "success", "tweet": text}
        except tweepy.TweepyException as e:
            if "duplicate content" in str(e).lower():
                logger.error(f"Tweet posting failed: Duplicate tweet - {text}")
                return {"status": "error", "message": "Tweet already posted!"}

            logger.error(f"Tweet posting failed: {e}")
            return {"status": "error", "message": str(e)}