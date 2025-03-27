from django.shortcuts import render
from django.http import JsonResponse
from .services import InstagramService, SummarizationService, XService
from datetime import datetime

def get_latest_post(request):
    """API endpoint to fetch the latest Instagram post from bbcnews."""
    service = InstagramService(username="bbcnews")
    post_data = service.fetch_latest_post()
    if post_data:
        return JsonResponse({"status": "success", "data": post_data})
    return JsonResponse({"status": "error", "message": "Failed to fetch Instagram post"}, status=500)

def post_tweet(request):
    """API endpoint to summarize and post the latest Instagram caption to X."""
    instagram_service = InstagramService(username="bbcnews")
    summary_service = SummarizationService()
    x_service = XService()

    post_data = instagram_service.fetch_latest_post()
    if not post_data:
        return JsonResponse({"status": "error", "message": "Failed to fetch Instagram post"}, status=500)

    summary = summary_service.summarize_caption(post_data["caption"])

    # Add time so it’s never the same
    summary = f"{summary} {datetime.now().strftime('%H:%M:%S')}"
    tweet_result = x_service.post_tweet(summary)


    # Check if base summary was posted before (simple check)
    last_summary = request.session.get('last_summary', None)
    if last_summary == summary:
        return JsonResponse({"status": "error", "message": "Tweet already posted!"})
    
    # Add time and post
    summary_with_time = f"{summary} {datetime.now().strftime('%H:%M:%S')}"
    tweet_result = x_service.post_tweet(summary_with_time)

    # Save the base summary for next time
    request.session['last_summary'] = summary

    return JsonResponse(tweet_result)