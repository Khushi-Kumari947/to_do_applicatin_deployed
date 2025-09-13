from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,EmailStr
from bson import ObjectId
from .database import users_collection, todos_collection
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(BaseModel):
    email: EmailStr
    password: str

class Todo(BaseModel):
    title: str
    description: str | None = None

class TodoUpdate(BaseModel):
    task_id: str
    title: str | None = None
    description: str | None = None

class TodoDelete(BaseModel):
    task_id: str

# -------------------- AUTH --------------------
@app.post("/register")
def register(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = pwd_context.hash(user.password)
    users_collection.insert_one({"email": user.email, "password": hashed_password})
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: User):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful"}

# -------------------- TODOS --------------------
@app.post("/todos/")
def create_task(todo: Todo, user_email: str):
    task = todo.dict()
    task["user_email"] = user_email
    result = todos_collection.insert_one(task)
    return {"task_id": str(result.inserted_id)}

@app.get("/todos/")
def get_tasks(user_email: str):
    tasks = list(todos_collection.find({"user_email": user_email}))
    for t in tasks:
        t["_id"] = str(t["_id"])
    return tasks

@app.put("/todos/")
def update_task(todo: TodoUpdate, user_email: str):
    update_data = {k: v for k, v in todo.dict().items() if v and k != "task_id"}
    result = todos_collection.update_one(
        {"_id": ObjectId(todo.task_id), "user_email": user_email},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully"}

@app.delete("/todos/")
def delete_task(todo: TodoDelete, user_email: str):
    result = todos_collection.delete_one({"_id": ObjectId(todo.task_id), "user_email": user_email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
