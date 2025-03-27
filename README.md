# Instagram Fetcher


A simple program to get Instagram posts and tweet them.

## How to Use
1. Install stuff: `pip install -r requirements.txt`
2. Start it: `python manage.py runserver`
3. Try buttons:
   - `http://127.0.0.1:8000/api/latest-post/` (get post)
   - `http://127.0.0.1:8000/api/post-tweet/` (post tweet)

## Needs
- Python 3
- Django, requests, selenium, transformers, tweepy (in `requirements.txt`)
- X.com keys in `services.py`

## Notes
- Instagram blocks us, so it uses fake data.
- Tweets real posts with your X.com keys.

A Django-based backend to fetch Instagram posts, summarize captions, and post to X.com.

## System Overview
- **Framework**: Django 5.1
- **Part 1**: Fetches the latest `bbcnews` Instagram post (caption + image URL) via scraping or simulation.
- **Part 2**: Summarizes captions using Hugging Face’s `bart-large-cnn` and posts to X.com (simulated).
- **Architecture**: Modular design with separate services for Instagram fetching, summarization, and X posting.

## Setup Instructions
1. Clone: `git clone <repo-url>`
2. Install: `pip install -r requirements.txt`
3. Run: `python manage.py migrate && python manage.py runserver`
4. (Optional) Install ChromeDriver for Selenium: [Download](https://sites.google.com/chromium.org/driver/)

## Requirements
- Python 3.x
- See `requirements.txt`

## API Endpoints
1. **GET /api/latest-post/**
   - Response: `{"status": "success", "data": {"caption": "...", "image_url": "..."}}`
   - Error: `{"status": "error", "message": "..."}`
2. **GET /api/post-tweet/**
   - Response: `{"status": "success", "tweet": "..."}`
   - Error: `{"status": "error", "message": "..."}`

## Configuration
- **Change Instagram Username**: Edit `views.py`:
  ```python
  service = InstagramService(username="new_username")

