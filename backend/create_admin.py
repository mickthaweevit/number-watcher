#!/usr/bin/env python3
"""
Create first admin user for NumWatch application
Run this script after database setup to create the initial admin account
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, engine
from app.models.user import User
from app.services.auth import get_password_hash
from sqlalchemy.orm import Session

# Admin credentials - CHANGE THESE IN PRODUCTION
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@numwatch.com"
ADMIN_PASSWORD = "admin123"  # Change this password!

def create_admin():
    """Create the first admin user"""
    
    # Create database tables if they don't exist
    from app.database import Base
    from app.models import user, dashboard_profile
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if existing_admin:
            print(f"❌ Admin user '{ADMIN_USERNAME}' already exists!")
            return False
        
        # Create admin user
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin_user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print("🔑 ADMIN CREDENTIALS:")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   Email: {ADMIN_EMAIL}")
        print("=" * 50)
        print("⚠️  IMPORTANT: Change the password after first login!")
        print("🌐 Login at: http://localhost:5173/login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating admin user for NumWatch...")
    success = create_admin()
    sys.exit(0 if success else 1)