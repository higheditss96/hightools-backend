import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HIGHTOOLS Kick API")

# === Allow frontend ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS Kick API active and ready"}

@app.get("/api/follows")
async def get_follows(username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1️⃣ Luăm informațiile canalului
            channel_url = f"https://kick.com/api/v1/channels/{username}"
            channel_response = await client.get(channel_url, headers=headers)

            if channel_response.status_code != 200:
                # Dacă Kick blochează cererea, încearcă prin proxy
                proxy_url = f"https://api.allorigins.win/raw?url={channel_url}"
                channel_response = await client.get(proxy_url, headers=headers)

            # Verificăm dacă răspunsul e JSON valid
            try:
                channel_data = channel_response.json()
            except Exception:
                raise HTTPException(status_code=500, detail="Invalid Kick API response (non-JSON)")

            channel_id = channel_data.get("id")
            if not channel_id:
                raise HTTPException(status_code=404, detail="Channel not found or missing ID")

            # 2️⃣ Luăm lista de follows
            follows_url = f"https://kick.com/api/v1/channels/{channel_id}/following"
            follows_response = await client.get(follows_url, headers=headers)

            if follows_response.status_code != 200:
                # Încearcă fallback prin proxy
                proxy_follows = f"https://api.allorigins.win/raw?url={follows_url}"
                follows_response = await client.get(proxy_follows, headers=headers)

            try:
                follows_data = follows_response.json()
            except Exception:
                raise HTTPException(status_code=500, detail="Invalid follows response (non-JSON)")

            return follows_data

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Kick API timeout (server too slow)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

