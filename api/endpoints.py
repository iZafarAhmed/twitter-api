# api/endpoints.py
from fastapi import APIRouter, Query, HTTPException
from core.twitter_client import run_twitter_command
import time  # Add this import at the top of the file if not already there

router = APIRouter()

@router.get("/feed")
async def get_feed(
    timeline_type: str = Query("for-you", regex="^(for-you|following)$"),
    max_tweets: int = Query(10, ge=1, le=50)
):
    """Get your Twitter timeline"""
    args = ["feed", "-t", timeline_type, "--max", str(max_tweets)]
    result = run_twitter_command(args)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/search")
async def search_tweets(
    query: str,
    max_results: int = Query(10, ge=1, le=50)
):
    """Search for tweets"""
    args = ["search", query, "--max", str(max_results)]
    result = run_twitter_command(args)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/user/{username}")
async def get_user_profile(username: str):
    """Get user profile info"""
    result = run_twitter_command(["user", username])
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/user/{username}/posts")
async def get_user_posts(
    username: str,
    max_posts: int = Query(10, ge=1, le=50)
):
    """Get recent posts from a specific user"""
    # Note: username should NOT include @ symbol
    args = ["user-posts", username, "--max", str(max_posts)]
    result = run_twitter_command(args)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/users/posts")
async def get_multiple_users_posts(
    users: str,  # Comma-separated: "user1,user2,user3"
    max_posts_per_user: int = Query(5, ge=1, le=20),
    include_user_info: bool = Query(True, description="Include user profile info with each tweet")
):
    """
    Get recent posts from multiple users in one request.
    
    Example: /api/v1/users/posts?users=MiddleEastEye,BBCNews,AlJazeera&max_posts_per_user=3
    """
    # Parse comma-separated usernames
    usernames = [u.strip() for u in users.split(",") if u.strip()]
    
    if not usernames:
        raise HTTPException(status_code=400, detail="Please provide at least one username")
    
    if len(usernames) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 users per request")
    
    results = {}
    errors = []
    
    # Fetch posts for each user (sequential to avoid rate limiting)
    for username in usernames:
        try:
            # Small delay to avoid triggering rate limits
            time.sleep(0.5)
            
            args = ["user-posts", username, "--max", str(max_posts_per_user)]
            result = run_twitter_command(args)
            
            if result["success"]:
                tweets = result.get("data", [])
                
                # Optionally add username to each tweet for easier parsing
                if include_user_info:
                    for tweet in tweets:
                        if isinstance(tweet, dict):
                            tweet["_source_user"] = username
                
                results[username] = {
                    "success": True,
                    "count": len(tweets),
                    "posts": tweets
                }
            else:
                results[username] = {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "posts": []
                }
                errors.append(f"{username}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            results[username] = {
                "success": False,
                "error": str(e),
                "posts": []
            }
            errors.append(f"{username}: {str(e)}")
    
    # Return structured response
    return {
        "success": len(errors) < len(usernames),  # Partial success is still "success"
        "requested_users": usernames,
        "results": results,
        "errors": errors if errors else None,
        "summary": {
            "total_users": len(usernames),
            "successful": len([u for u in results.values() if u["success"]]),
            "failed": len(errors),
            "total_posts": sum(r["count"] for r in results.values() if r["success"])
        }
    }

@router.get("/health")
async def health_check():
    """Check if API is running"""
    return {"status": "ok", "service": "twitter-api"}