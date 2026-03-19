from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import User, UserRole
from auth import hash_password
from routes import auth, users, admin

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Multi-Finance Tracker API",
    description="API for tracking income and expenses across multiple financial contexts",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
def read_root():
    """Root endpoint of the API"""
    return {
        "name": "Multi-Finance Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
def create_default_admin():
    """Create a default admin user on startup if it doesn't exist"""
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin_exists:
            default_admin = User(
                email="admin@mft.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=hash_password("admin123"),  # Change this!
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(default_admin)
            db.commit()
            print("✓ Default admin created with email: admin@mft.com")
            print("  Password: admin123 (please change this)")
        else:
            print("✓ Admin user already exists")
    except Exception as e:
        print(f"✗ Error creating default admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
