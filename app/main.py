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


@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS Kick API v2 Active"}


# === 1️⃣ GET USER INFO ===
@app.get("/user")
async def get_user(username: str):
    """
    Obține date despre un user Kick (folosind /api/v2/channels/{username})
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
        return res.json()


# === 2️⃣ GET USER FOLLOWS ===
@app.get("/follows")
async def get_follows(username: str):
    """
    Returnează lista de follows pentru un user public Kick.
    """
    async with httpx.AsyncClient() as client:
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res_user.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")

        user = res_user.json()
        user_id = user["user_id"]

        res_follows = await client.get(f"{KICK_API_BASE}/users/{user_id}/following")
        if res_follows.status_code != 200:
            raise HTTPException(status_code=res_follows.status_code, detail=res_follows.text)

        return {"user": user, "follows": res_follows.json()}


# === 3️⃣ COMPARE FOLLOWS ===
@app.get("/compare")
async def compare_follows(user1: str, user2: str):
    async with httpx.AsyncClient() as client:
        res1 = await client.get(f"{KICK_API_BASE}/channels/{user1.lower()}")
        res2 = await client.get(f"{KICK_API_BASE}/channels/{user2.lower()}")

        if res1.status_code != 200 or res2.status_code != 200:
            raise HTTPException(status_code=404, detail="One or both users not found")

        u1 = res1.json()
        u2 = res2.json()

        res_f1 = await client.get(f"{KICK_API_BASE}/users/{u1['user_id']}/following")
        res_f2 = await client.get(f"{KICK_API_BASE}/users/{u2['user_id']}/following")

        if res_f1.status_code != 200 or res_f2.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch follows")

        f1 = res_f1.json()
        f2 = res_f2.json()

        mutuals = [
            ch for ch in f1
            if any(ch["username"].lower() == c2["username"].lower() for c2 in f2)
        ]

        return {"user1": u1, "user2": u2, "mutuals": mutuals, "count": len(mutuals)}
