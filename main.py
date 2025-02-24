from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import json
import os
import time  # Import to add delay for database connection

# Initialize FastAPI
app = FastAPI()

# Base for Models
Base = declarative_base()

# Function to Get Engine and SessionLocal
def get_engine_and_session():
    TESTING = os.getenv("TESTING", "False") == "True"

    if TESTING:
        # Use SQLite for Testing
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test_orders.db"
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        # Use PostgreSQL for Production/Docker
        POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "orders")
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")  # Docker Compose Service Name
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

        SQLALCHEMY_DATABASE_URL = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Create SessionLocal with Scoped Session for Thread Safety
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    return engine, SessionLocal

# Lazy Load Engine and SessionLocal
engine, SessionLocal = get_engine_and_session()

# Models
class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer)
    order_type = Column(String)
    status = Column(String, default="pending")

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected_clients.append(connection)

        # Remove disconnected clients
        for client in disconnected_clients:
            self.disconnect(client)

manager = ConnectionManager()

# Endpoints

# Get All Orders
@app.get("/orders/")
def get_orders(db=Depends(get_db)):
    orders = db.query(Order).all()
    return orders

# Create Order and Notify WebSocket Clients
@app.post("/orders/")
async def create_order(order: dict, db=Depends(get_db)):
    db_order = Order(
        symbol=order["symbol"],
        price=order["price"],
        quantity=order["quantity"],
        order_type=order["order_type"],
        status=order.get("status", "pending")  # Default to "pending" if not specified
    )
    db.add(db_order)
    db.commit()  # Explicit Commit
    db.refresh(db_order)  # Refresh to get ID

    # Broadcast new order status as "pending"
    await manager.broadcast(json.dumps({"order_id": db_order.id, "status": db_order.status}))
    return {
        "id": db_order.id,
        "symbol": db_order.symbol,
        "price": db_order.price,
        "quantity": db_order.quantity,
        "order_type": db_order.order_type,
        "status": db_order.status
    }

# Update Order Status and Notify WebSocket Clients
@app.put("/orders/{order_id}")
async def update_order(order_id: int, status: str, db=Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    db_order.status = status
    db.commit()  # Commit the Update
    db.refresh(db_order)  # Refresh to Reflect Changes

    # Broadcast updated order status
    await manager.broadcast(json.dumps({"order_id": db_order.id, "status": db_order.status}))
    return {
        "id": db_order.id,
        "symbol": db_order.symbol,
        "price": db_order.price,
        "quantity": db_order.quantity,
        "order_type": db_order.order_type,
        "status": db_order.status
    }

# WebSocket Endpoint for Real-Time Updates
@app.websocket("/ws/orders/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Static Files and Home Page
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    return HTMLResponse(open("static/index.html").read())

# Startup Event to Create Tables Automatically
@app.on_event("startup")
def on_startup():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
            break
        except Exception as e:
            print(f"Error creating tables: {e}")
            retries -= 1
            print(f"Retrying in 5 seconds... ({retries} retries left)")
            time.sleep(5)
