from fastapi import FastAPI
from search import search

app = FastAPI()

@app.get("/search")
def search_endpoint(q: str):
    return search(q)
