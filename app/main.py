import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode

# === Kick App Credentials (from Railway or .env) ===
KICK_CLIENT_ID = os.getenv("KICK_CLIENT_ID")
KICK_CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")
KICK_REDIRECT_URI = os.getenv("KICK_REDIRECT_URI")

KICK_AUTH_URL = "https://kick.com/oauth/authorize"
KICK_TOKEN_URL = "https://kick.com/oauth/token"
KICK_API_URL = "https://api.kick.com/v1"

app = FastAPI(title="HIGHTOOLS Official Kick API")

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # înlocuiește cu frontend-ul tău când e gata
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "✅ HIGHTOOLS official Kick API active"}

@app.get("/login")
def login():
    """Redirect user to Kick OAuth login"""
    params = {
        "client_id": KICK_CLIENT_ID,
        "redirect_uri": KICK_REDIRECT_URI,
        "response_type": "code",
        "scope": "user.read channels.read",
    }
    url = f"{KICK_AUTH_URL}?{urlencode(params)}"
    return {"auth_url": url}

@app.get("/callback")
async def callback(code: str):
    """Exchange the OAuth code for an access token"""
    async with httpx.AsyncClient() as client:
        payload = {
            "client_id": KICK_CLIENT_ID,
            "client_secret": KICK_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": KICK_REDIRECT_URI,
            "code": code,
        }
        response = await client.post(KICK_TOKEN_URL, data=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    return {
        "access_token": data.get("access_token"),
        "expires_in": data.get("expires_in"),
    }

@app.get("/me")
async def get_user_info(token: str):
    """Fetch authenticated user's info"""
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{KICK_API_URL}/users/@me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()

@app.get("/follows")
async def get_user_following(channel_id: str, token: str):
    """Get list of channels the user follows"""
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{KICK_API_URL}/channels/{channel_id}/following",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
