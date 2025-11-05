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


# === 1️⃣ GET USER INFO ===
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


# === 2️⃣ GET FOLLOWS ===
@app.get("/follows")
async def get_follows(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        # === 1️⃣ Ia user info
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

        # === 2️⃣ Endpoint principal
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


# === 4️⃣ DEBUG ENDPOINT ===
@app.get("/debug")
async def debug_raw(username: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        res_user = await client.get(f"{KICK_API_BASE}/channels/{username.lower()}")
        if res_user.status_code != 200:
            return {"status": res_user.status_code, "body": res_user.text}

        user = res_user.json()
        user_id = user.get("user_id")

        results = {}

        # încearcă endpointurile posibile
        urls = [
            f"{KICK_API_BASE}/users/{user_id}/following",
            f"{KICK_API_BASE}/channels/{username.lower()}/following",
            f"https://kick.com/api/v2/users/{user_id}/following",
            f"https://kick.com/api/v1/users/{user_id}/following"
        ]

        for url in urls:
            try:
                r = await client.get(url)
                results[url] = {
                    "status": r.status_code,
                    "body": r.text[:500]  # doar primele 500 caractere
                }
            except Exception as e:
                results[url] = {"error": str(e)}

        return {
            "checked_user": user,
            "tested_urls": urls,
            "results": results
        }
