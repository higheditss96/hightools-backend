import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HIGHTOOLS Kick Public API v2")

KICK_API_BASE = "https://kick.com/api/v2"

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/129.0 Safari/537.36",
    "Accept": "application/json",
}


@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS Kick API v2 Active"}


# === 1️⃣ USER INFO ===
@app.get("/user")
async def get_user(username: str):
    async with httpx.AsyncClient(headers=HEADERS) as client:
        res = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 2️⃣ FOLLOWING LIST ===
@app.get("/follows")
async def get_follows(username: str):
    async with httpx.AsyncClient(headers=HEADERS) as client:
        # 1️⃣ Obținem info despre canal (inclusiv user_id)
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res_user.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")

        user = res_user.json()
        user_id = user.get("user_id")

        if not user_id:
            raise HTTPException(status_code=404, detail="Invalid user data")

        # 2️⃣ Obținem following list
        res_follows = await client.get(f"{KICK_API_BASE}/users/{user_id}/following")
        if res_follows.status_code != 200:
            raise HTTPException(status_code=res_follows.status_code, detail=res_follows.text)

        return {"user": user, "follows": res_follows.json()}


# === 3️⃣ COMPARE FOLLOWS ===
@app.get("/compare")
async def compare(user1: str, user2: str):
    async with httpx.AsyncClient(headers=HEADERS) as client:
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
