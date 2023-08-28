import json
import httpx
import uvicorn
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse

# local imports
import ingredients


app = FastAPI(
    title="Ingredients – API",
    license_info="https://github.com/berrysauce/ingredients/blob/main/LICENSE.md",
    docs_url=None,
    redoc_url=None
)

origins = [
    "*.berrysauce.me",
    "*.ingredients.tech"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def get_root():
    with open("pages/api.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/ingredients", response_class=JSONResponse)
def get_scan(url: str, response: Response, includeCategories: Optional[bool] = False):
    
    # Parse URL and remove port, query, and fragment
    r = urlparse(url)
    parsed_url = r.scheme + "://" + r.netloc.split(":")[0] + r.path
    
    try:        
        data = ingredients.scan(parsed_url)
        if includeCategories:
            with open("ingredients/categories.json", "r") as f:
                data["categories"] = json.loads(f.read())
        return data
    except httpx.InvalidURL as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": str(e)
        }
    except httpx.RequestError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": str(e)
        }
    except:
        raise HTTPException(status_code=500, detail="Unknown error")
        
        
@app.get("/icon/{icon}")
def get_icon(icon: str, response: Response):
    # increase compatibility
    if ".png" not in icon:
        icon += ".png"
        
    # parse icon and remove path, query, and fragment
    parsed_icon = icon.lower().split("/")[0].split("?")[0].split("#")[0]
    
    try:
        with open("./icons/" + parsed_icon, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    except FileNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "error": "Icon not found"
        }
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "An error occured while fetching the icon"
        }
        


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)