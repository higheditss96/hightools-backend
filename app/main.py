import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HIGHTOOLS Kick Public API v2")

KICK_API_BASE = "https://kick.com/api/v2"

# === ✅ CORS pentru domeniul tău Vercel ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hightools-frontend.vercel.app",     # frontend-ul tău live
        "https://www.hightools-frontend.vercel.app", # fallback subdomeniu
        "http://localhost:3000",                     # dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === HEADERE pentru Kick API ===
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# === ROOT TEST ===
@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS Kick API v2 Active"}


# === 1️⃣ GET USER INFO ===
@app.get("/user")
async def get_user(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        res = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 2️⃣ GET FOLLOWING LIST (cu fallback și erori clare) ===
@app.get("/follows")
async def get_follows(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        # 1️⃣ Obține datele userului
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res_user.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if res_user.status_code != 200:
            raise HTTPException(status_code=res_user.status_code, detail=res_user.text)

        user = res_user.json()
        user_id = user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=502, detail="Invalid user data from Kick")

        # Helper pentru interpretare erori
        async def _raise_for_status(resp: httpx.Response, fallback: bool):
            if resp.status_code == 200:
                return
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Following list hidden or not found")
            if resp.status_code == 403:
                raise HTTPException(status_code=403, detail="This profile is private")
            if resp.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limited by Kick. Please try again soon")
            if not fallback:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)

        # 2️⃣ Prima încercare — /users/{id}/following
        res_follow_1 = await client.get(f"{KICK_API_BASE}/users/{user_id}/following")
        if res_follow_1.status_code == 200:
            return {"user": user, "follows": res_follow_1.json()}

        await _raise_for_status(res_follow_1, fallback=True)

        # 3️⃣ Fallback — /channels/{username}/following
        res_follow_2 = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}/following")
        await _raise_for_status(res_follow_2, fallback=False)

        return {"user": user, "follows": res_follow_2.json()}


# === 3️⃣ COMPARE FOLLOWS ===
@app.get("/compare")
async def compare(user1: str, user2: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        res1 = await client.get(f"{KICK_API_BASE}/channels/{user1.lower()}")
        res2 = await client.get(f"{KICK_API_BASE}/channels/{user2.lower()}")

        if res1.status_code != 200 or res2.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")

        u1, u2 = res1.json(), res2.json()
        res_f1 = await client.get(f"{KICK_API_BASE}/users/{u1['user_id']}/following")
        res_f2 = await client.get(f"{KICK_API_BASE}/users/{u2['user_id']}/following")

        if res_f1.status_code != 200 or res_f2.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get follows")

        f1, f2 = res_f1.json(), res_f2.json()

        mutuals = [
            ch for ch in f1
            if any(ch["username"].lower() == c2["username"].lower() for c2 in f2)
        ]

        return {"user1": u1, "user2": u2, "mutuals": mutuals, "count": len(mutuals)}
