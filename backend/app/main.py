from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.app.routes import stock

app = FastAPI(
    title ="Agentic AI Stock Research Assistant",
    version="1.0.0"
)

# Standard FastAPI Convention to Serve CSS, JS, images
app.mount(
    "/static",
    StaticFiles(directory="backend/app/static"),
    name ="static"
)

#Standard FastAPI convention to serve HTML Templates
templates = Jinja2Templates(
    directory="backend/app/templates"
)
@app.get("/")
async def home(request:Request):
    return templates.TemplateResponse(
        name="index.html",
        request=request
    )
        

@app.get("/health")
async def health():
    return {
        "status":"healthy"
    }

app.include_router(stock.router)