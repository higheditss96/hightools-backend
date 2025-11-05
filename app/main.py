import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode

app = FastAPI(title="HIGHTOOLS Kick Follows")

# === CONFIG ===
KICK_CLIENT_ID = os.getenv("KICK_CLIENT_ID")
KICK_CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")
KICK_REDIRECT_URI = os.getenv(
    "KICK_REDIRECT_URI",
    "https://hightools-backend-production.up.railway.app/callback"
)

KICK_AUTH_URL = "https://kick.com/oauth/authorize"
KICK_TOKEN_URL = "https://kick.com/oauth/token"
KICK_API_URL = "https://api.kick.com/v1"

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # poți restricționa ulterior doar la domeniul frontendului tău
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === ROOT ===
@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS API Active"}


# === 1️⃣ LOGIN REDIRECT ===
@app.get("/login")
def login():
    params = {
        "client_id": KICK_CLIENT_ID,
        "redirect_uri": KICK_REDIRECT_URI,
        "response_type": "code",
        "scope": "user.read follows.read channels.read",
    }
    return {"auth_url": f"{KICK_AUTH_URL}?{urlencode(params)}"}


# === 2️⃣ CALLBACK TOKEN ===
@app.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        payload = {
            "client_id": KICK_CLIENT_ID,
            "client_secret": KICK_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": KICK_REDIRECT_URI,
            "code": code,
        }
        res = await client.post(KICK_TOKEN_URL, data=payload)

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        return res.json()


# === 3️⃣ GET AUTH USER INFO ===
@app.get("/me")
async def get_me(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_URL}/users/@me", headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 4️⃣ GET USER FOLLOWS ===
@app.get("/follows")
async def get_user_follows(user_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_URL}/users/{user_id}/following", headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 5️⃣ SEARCH USER BY USERNAME ===
@app.get("/user")
async def search_user(username: str, token: str):
    """
    Returnează detalii despre un utilizator Kick după username.
    """
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_URL}/users/{username}", headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 6️⃣ COMPARE FOLLOWS ===
@app.get("/compare")
async def compare_follows(user1_id: str, user2_id: str, token: str):
    """
    Compară lista de follows dintre două conturi și returnează mutuals.
    """
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res1 = await client.get(f"{KICK_API_URL}/users/{user1_id}/following", headers=headers)
        res2 = await client.get(f"{KICK_API_URL}/users/{user2_id}/following", headers=headers)

        if res1.status_code != 200 or res2.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch follows for comparison")

        follows1 = res1.json()
        follows2 = res2.json()

        # comparăm după username (case-insensitive)
        mutuals = [
            ch for ch in follows1
            if any(ch["username"].lower() == f2["username"].lower() for f2 in follows2)
        ]

        return {"mutuals": mutuals, "count": len(mutuals)}


# === 1️⃣ LOGIN REDIRECT ===
@app.get("/login")
def login():
    params = {
        "client_id": KICK_CLIENT_ID,
        "redirect_uri": KICK_REDIRECT_URI,
        "response_type": "code",
        "scope": "user.read follows.read channels.read",
    }
    return {"auth_url": f"{KICK_AUTH_URL}?{urlencode(params)}"}


# === 2️⃣ CALLBACK TOKEN ===
@app.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        payload = {
            "client_id": KICK_CLIENT_ID,
            "client_secret": KICK_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": KICK_REDIRECT_URI,
            "code": code,
        }
        res = await client.post(KICK_TOKEN_URL, data=payload)

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        return res.json()


# === 3️⃣ GET AUTH USER INFO ===
@app.get("/me")
async def get_me(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_URL}/users/@me", headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 4️⃣ GET USER FOLLOWS ===
@app.get("/follows")
async def get_user_follows(user_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_URL}/users/{user_id}/following", headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 5️⃣ SEARCH USER BY USERNAME ===
@app.get("/user")
async def search_user(username: str, token: str):
    """
    Returnează detalii despre un utilizator Kick după username.
    """
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{KICK_API_URL}/users/{username}", headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()


# === 6️⃣ COMPARE FOLLOWS ===
@app.get("/compare")
async def compare_follows(user1_id: str, user2_id: str, token: str):
    """
    Compară lista de follows dintre două conturi și returnează mutuals.
    """
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        res1 = await client.get(f"{KICK_API_URL}/users/{user1_id}/following", headers=headers)
        res2 = await client.get(f"{KICK_API_URL}/users/{user2_id}/following", headers=headers)

        if res1.status_code != 200 or res2.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch follows for comparison")

        follows1 = res1.json()
        follows2 = res2.json()

        # comparăm după username (case-insensitive)
        mutuals = [
            ch for ch in follows1
            if any(ch["username"].lower() == f2["username"].lower() for f2 in follows2)
        ]

        return {"mutuals": mutuals, "count": len(mutuals)}
