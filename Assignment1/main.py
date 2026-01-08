from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from models import User
import crud

app = FastAPI(title="FastAPI + MongoDB CRUD (AI Eng)")

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/users")
def create_user(user: User):
    crud.create_user(user.dict())
    return {"message": "User created successfully"}

@app.get("/users")
def read_users():
    return crud.get_all_users()

@app.get("/users/{name}")
def read_user(name: str):
    user = crud.get_user_by_name(name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{name}")
def update_user(name: str, update_data: dict):
    result = crud.update_user(name, update_data)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated"}

@app.delete("/users/{name}")
def delete_user(name: str):
    result = crud.delete_user(name)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
