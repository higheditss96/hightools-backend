import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HIGHTOOLS Kick API v2 Stable")

KICK_API_BASE = "https://kick.com/api/v2"

# === CORS pentru Vercel ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hightools-frontend.vercel.app",
        "https://www.hightools-frontend.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS Kick API v2 Active"}


@app.get("/user")
async def get_user(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        res = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        try:
            return res.json()
        except Exception:
            raise HTTPException(status_code=502, detail="Invalid response from Kick API")


@app.get("/follows")
async def get_follows(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        # === 1️⃣ Ia datele userului
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res_user.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if res_user.status_code != 200:
            raise HTTPException(status_code=res_user.status_code, detail=res_user.text)

        try:
            user = res_user.json()
        except Exception:
            raise HTTPException(status_code=502, detail="Invalid user response")

        user_id = user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=502, detail="Missing user_id from Kick response")

        # === 2️⃣ Încearcă endpointul principal
        res_follow_1 = await client.get(f"{KICK_API_BASE}/users/{user_id}/following")

        if res_follow_1.status_code == 200:
            try:
                data = res_follow_1.json()
                if isinstance(data, dict) and "message" in data and data["message"] == "Not Found":
                    raise HTTPException(status_code=404, detail="Following list hidden or not found")
                return {"user": user, "follows": data}
            except Exception:
                raise HTTPException(status_code=502, detail="Invalid follow list from Kick")

        # === 3️⃣ Fallback — /channels/{username}/following
        res_follow_2 = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}/following")

        if res_follow_2.status_code == 200:
            try:
                data2 = res_follow_2.json()
                return {"user": user, "follows": data2}
            except Exception:
                raise HTTPException(status_code=502, detail="Invalid follow fallback from Kick")

        # === 4️⃣ Alte cazuri
        if res_follow_2.status_code == 404:
            raise HTTPException(status_code=404, detail="Following list hidden or not found")
        if res_follow_2.status_code == 403:
            raise HTTPException(status_code=403, detail="This profile is private")
        if res_follow_2.status_code == 429:
            raise HTTPException(status_code=429, detail="Rate limited by Kick. Try again soon.")

        raise HTTPException(status_code=res_follow_2.status_code, detail="Unexpected error from Kick API")
