from fastapi import FastAPI

app = FastAPI(title="Part Buddy API", version="0.0.1")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "part-buddy", "version": "0.0.1"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
