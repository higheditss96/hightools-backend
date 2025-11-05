import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HIGHTOOLS Kick API v2 Public")

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


# === 1️⃣ GET USER INFO (stabil) ===
@app.get("/user")
async def get_user(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        res = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        try:
            return res.json()
        except Exception:
            raise HTTPException(status_code=502, detail="Invalid response from Kick API")


# === 2️⃣ FOLLOWERS / FOLLOWING (temporar limitat) ===
@app.get("/follows")
async def get_follows(username: str):
    """
    În prezent Kick a restricționat endpointul /users/{id}/following.
    Returnăm datele de bază ale canalului și un mesaj informativ.
    """
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res_user.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if res_user.status_code != 200:
            raise HTTPException(status_code=res_user.status_code, detail=res_user.text)
        user = res_user.json()
        return {
            "user": user,
            "follows": [],
            "message": "Kick API v2 a făcut lista de follows privată. Date limitate disponibile.",
        }


# === 3️⃣ DEBUG ENDPOINT ===
@app.get("/debug")
async def debug_raw(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        user_id = None
        if res_user.status_code == 200:
            try:
                user = res_user.json()
                user_id = user.get("user_id")
            except Exception:
                user = res_user.text
        else:
            user = {"error": res_user.text}

        urls = [
            f"{KICK_API_BASE}/channels/{username.lower()}",
            f"{KICK_API_BASE}/users/{user_id}/following" if user_id else None,
            f"https://kick.com/api/v1/users/{user_id}/following" if user_id else None,
            f"https://kick.com/@{username.lower()}",
        ]
        urls = [u for u in urls if u]

        results = {}
        for url in urls:
            try:
                r = await client.get(url)
                results[url] = {
                    "status": r.status_code,
                    "type": r.headers.get("content-type"),
                    "body_preview": r.text[:300],
                }
            except Exception as e:
                results[url] = {"error": str(e)}

        return {"checked_user": user, "tested_urls": urls, "results": results}
