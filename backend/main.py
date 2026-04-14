from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import User, UserRole
from auth import hash_password
from routes import auth, users, admin, entity, categories, transactions, reports, transactions

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multi-Finance Tracker API",
    description="Track income and expenses across multiple financial entities",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(entity.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {"name": "Multi-Finance Tracker API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            default_admin = User(
                email="admin@mft.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(default_admin)
            db.commit()
            print("✓ Default admin created — email: admin@mft.com / password: admin123")
    except Exception as e:
        print(f"✗ Error creating default admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
