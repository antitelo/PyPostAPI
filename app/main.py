import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

class Post(BaseModel):
    title: str
    content: str
    published: bool

while True:
    try:
        conn =  psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, cursor_factory=RealDictCursor
            )
        cursor = conn.cursor()
        print("db was connected")
        break
    except Exception as error:
        print("connection failed")
        print("Error:", error)
        time.sleep(2)

app = FastAPI(title="PyPostAPI", version="0.1.0")


@app.get("/")
def get_root():
    return {"message": "hello world", "docs": "/docs"}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"message": f"post {new_post} was created"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    if post:
        return {"post_detail": post}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        

@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, updated_post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                    (updated_post.title, updated_post.content, updated_post.published, str(id)))
    updated = cursor.fetchone()
    conn.commit()
    if updated:
        return {"message": f"post {id} was updated"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
