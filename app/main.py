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
    """Get public info about a Kick user (fallback since Kick blocked following list)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0 Safari/537.36",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Cerem informațiile de canal
        channel_url = f"https://kick.com/api/v1/channels/{username}"
        response = await client.get(channel_url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found on Kick")

        try:
            data = response.json()
        except Exception:
            raise HTTPException(status_code=500, detail="Invalid Kick API response (non-JSON)")

        # Returnăm doar informațiile utile
        return {
            "username": data.get("slug"),
            "id": data.get("id"),
            "followers": data.get("followersCount"),
            "category": data.get("recent_categories", []),
            "bio": data.get("user", {}).get("bio"),
            "profile_pic": data.get("user", {}).get("profile_pic"),
            "banner_image": data.get("banner_image"),
            "country": data.get("user", {}).get("country"),
            "joined": data.get("created_at"),
        }
