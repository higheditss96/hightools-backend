from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="HIGHTOOLS Public Kick API")

# ✅ CORS pentru Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sau ["https://hightools.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "HIGHTOOLS public Kick API active ✅"}

@app.get("/api/follows")
async def get_follows(username: str):
    """
    Returnează lista de persoane urmărite de un user Kick (neautentificat)
    """
    url = f"https://kick.com/api/v2/channels/{username}/following"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": f"https://kick.com/{username}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Kick API error")
            
            data = response.json()
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
