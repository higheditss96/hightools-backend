from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="HIGHTOOLS API")

# ✅ CORS (permite accesul de la Vercel și local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://hightools.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "HIGHTOOLS API is running"}

@app.get("/api/follows")
async def get_follows(username: str):
    """Returnează lista de utilizatori urmăriți pe Kick"""
    url = f"https://kick.com/api/v1/channels/{username}/following"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # Încearcă să convertești în JSON
            try:
                return response.json()
            except Exception:
                # Dacă nu e JSON, trimite textul brut (debug)
                return {"error": "Non-JSON response", "text": response.text[:500]}

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")