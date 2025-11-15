from typing import Optional

from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func

from .database import engine, init_db
from .models import Item
from .api.canvas import router as canvas_router

app = FastAPI(title="FastAPI + SQLite (SQLModel) example")

app.include_router(canvas_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"ok": True, "message": "FastAPI + SQLite (SQLModel)", "docs": "/docs"}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/health")
def health():
    try:
        # quick DB reachability check
        with Session(engine) as session:
            session.exec(select(Item).limit(1)).first()
        return {"ok": True, "database": "reachable"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/items/", response_model=Item)
def create_item(item: Item):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.get("/items/", response_model=list[Item])
def read_items():
    with Session(engine) as session:
        statement = select(Item)
        items = session.exec(statement).all()
        return items


@app.get("/items/count")
def items_count():
    with Session(engine) as session:
        count = session.exec(select(func.count()).select_from(Item)).one()
        return {"count": count}


@app.get("/items/search", response_model=list[Item])
def search_items(q: Optional[str] = None, name: Optional[str] = None):
    with Session(engine) as session:
        stmt = select(Item)
        if q:
            stmt = stmt.where((Item.name.contains(q)) | (Item.description.contains(q)))
        if name:
            stmt = stmt.where(Item.name == name)
        items = session.exec(stmt).all()
        return items


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item_data: Item):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item.name = item_data.name
        item.description = item_data.description
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(item)
        session.commit()
        return {"ok": True}
