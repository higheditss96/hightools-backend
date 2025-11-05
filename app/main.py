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
    return {"message": "✅ HIGHTOOLS Kick API active"}

@app.get("/api/follows")
async def get_follows(username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0 Safari/537.36",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1️⃣ Căutăm canalul
        channel_url = f"https://kick.com/api/v1/channels/{username}"
        response = await client.get(channel_url, headers=headers)

        if response.status_code != 200:
            # Dacă Kick blochează cererea, încearcă prin proxy
            proxy_url = f"https://api.allorigins.win/raw?url={channel_url}"
            proxy_response = await client.get(proxy_url, headers=headers)

            if proxy_response.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")

            data = proxy_response.json()
        else:
            data = response.json()

        channel_id = data.get("id")
        if not channel_id:
            raise HTTPException(status_code=404, detail="Channel ID not found")

        # 2️⃣ Luăm lista de follows
        follows_url = f"https://kick.com/api/v1/channels/{channel_id}/following"
        follows_response = await client.get(follows_url, headers=headers)

        if follows_response.status_code != 200:
            # Fallback la proxy dacă e blocat direct
            proxy_follows = f"https://api.allorigins.win/raw?url={follows_url}"
            proxy_resp = await client.get(proxy_follows, headers=headers)

            if proxy_resp.status_code != 200:
                raise HTTPException(status_code=proxy_resp.status_code, detail="Failed to fetch follows")

            return proxy_resp.json()

        return follows_response.json()
