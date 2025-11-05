from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="HIGHTOOLS API", version="1.0")

# Allow requests from your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "HIGHTOOLS API is running"}

@app.get("/api/follows")
async def get_follows(username: str):
    url = f"https://kick.com/api/v1/channels/{username}/following"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    return response.json()

            # Check if proxy returned 'contents'
            if isinstance(data, dict) and "contents" in data:
                import json
                return json.loads(data["contents"])

            # If already JSON data
            return data

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Proxy decode error: {e}")
