from fastapi import FastAPI

from calc_views import router as calc_router
from item_views import router as item_router
from users.views import router as user_router


app = FastAPI()
app.include_router(user_router, tags=["users"])
app.include_router(calc_router, tags=["calc"])
app.include_router(item_router, prefix="/items-new", tags=["items-new"])
    

@app.get("/")
def start():
    return {"message2": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
    