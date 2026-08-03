from fastapi import FastAPI

app = FastAPI(
    title ="Agentic AI Stock Research Assistant",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message" : " Welcome to Agentic AI Stock Research Assistant"
    }

@app.get("/health")
def health():
    return {
        "status":"healthy"
    }