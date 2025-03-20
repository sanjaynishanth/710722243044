from fastapi import FastAPI, HTTPException, Query
import requests
import json

# Initialize FastAPI
app = FastAPI()

#handiling redis the redis is used to store the data in the cache 
try:
    import redis
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    redis_available = True
except ImportError:
    redis_available = False

# API
USERS_API = "https://20.44.56.144/test/users"
POSTS_API = "https://20.44.56.144/test/users/:userid/posts"


JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQyNDU4MDE0LCJpYXQiOjE3NDI0NTc3MTQsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjNkN2E0ZDQyLTA0NTctNDIyYi05NWMwLWU3NjZiOWRhOGJhYSIsInN1YiI6IjIyYWQwNDRAZHJuZ3BpdC5hYy5pbiJ9LCJjb21wYW55TmFtZSI6IkRyLk4uRy5QIEluc3RpdHV0ZSBvZiBUZWNobm9sb2d5IiwiY2xpZW50SUQiOiIzZDdhNGQ0Mi0wNDU3LTQyMmItOTVjMC1lNzY2YjlkYThiYWEiLCJjbGllbnRTZWNyZXQiOiJGQWpmYlhMYkhLRHRma3l0Iiwib3duZXJOYW1lIjoiU2FuamF5IFMiLCJvd25lckVtYWlsIjoiMjJhZDA0NEBkcm5ncGl0LmFjLmluIiwicm9sbE5vIjoiNzEwNzIyMjQzMDQ0In0.oAHCdbgjWvUSTf7QXkHXOejIVEPyzn4f4sq7UAG_bbE"


HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

@app.get("/users")
def get_top_users():
    """
    Fetches the top 5 users with the highest number of posts.
    Uses Redis caching for performance optimization.
    """
    cache_key = "top_users"

    # Check Redis cache 
    if redis_available:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            print("Warning: Redis unavailable, proceeding without cache.")

    try:
        # Fetch user data from external API 
        response = requests.get(USERS_API, headers=HEADERS, timeout=5)
        response.raise_for_status()
        users = response.json()

        # Sort users 
        top_users = sorted(users, key=lambda x: x.get("post_count", 0), reverse=True)[:5]

        # return data from cache
        if redis_available:
            redis_client.setex(cache_key, 600, json.dumps(top_users))

        return top_users

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=502, detail="Error fetching users data from API")


@app.get("/posts")
def get_posts(type: str = Query("latest", enum=["latest", "popular"])):
    """
    Fetches posts based on query type:
    - `latest`: Fetches the latest 5 posts
    - `popular`: Fetches posts with the highest comment count
    """
    cache_key = f"posts_{type}"

    # Check Redis cache
    if redis_available:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            print("Warning: Redis unavailable, proceeding without cache.")

    try:
        # Fetch posts from external API 
        response = requests.get(POSTS_API, headers=HEADERS, timeout=5)
        response.raise_for_status()
        posts = response.json()

        if type == "latest":
            
            result_posts = sorted(posts, key=lambda x: x.get("timestamp", 0), reverse=True)[:5]
        else:
            
            max_comments = max(post.get("comment_count", 0) for post in posts)
            result_posts = [post for post in posts if post.get("comment_count", 0) == max_comments]

        
        if redis_available:
            redis_client.setex(cache_key, 600, json.dumps(result_posts))

        return result_posts

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=502, detail="Error fetching posts data from API")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
