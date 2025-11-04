from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="HIGHTOOLS API", version="1.0")

# Allow requests from your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "HIGHTOOLS API is running"}

@app.get("/api/follows")
async def get_follows(username: str):
    """
    Fetch following list for a Kick user — via proxy to bypass Cloudflare.
    """
    url = f"https://kick.com/api/v2/channels/{username}/following"
    proxy_url = f"https://api.codetabs.com/v1/proxy/?quest={url}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://kick.com/",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(proxy_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Kick proxy error")

            data = response.json()

            # Check if proxy returned 'contents'
            if isinstance(data, dict) and "contents" in data:
                import json
                return json.loads(data["contents"])

            # If already JSON data
            return data

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Proxy decode error: {e}")
