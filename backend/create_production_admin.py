#!/usr/bin/env python3
"""
Create admin user for production deployment
Run this after deploying to production
"""

import sys
import os
import secrets
import string

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, engine
from app.models.user import User
from app.services.auth import get_password_hash
from sqlalchemy.orm import Session

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_production_admin():
    """Create admin user for production"""
    
    # Create database tables if they don't exist
    from app.database import Base
    from app.models import user, dashboard_profile, invite_code
    Base.metadata.create_all(bind=engine)
    
    # Generate secure credentials
    admin_username = "admin"
    admin_email = "admin@numwatch.app"
    admin_password = generate_secure_password()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        if existing_admin:
            print(f"❌ Admin user '{admin_username}' already exists!")
            return False
        
        # Create admin user
        hashed_password = get_password_hash(admin_password)
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Production admin user created successfully!")
        print("=" * 60)
        print("🔑 PRODUCTION ADMIN CREDENTIALS:")
        print(f"   Username: {admin_username}")
        print(f"   Password: {admin_password}")
        print(f"   Email: {admin_email}")
        print("=" * 60)
        print("⚠️  IMPORTANT: Save these credentials securely!")
        print("⚠️  This password will not be shown again!")
        print("🌐 Login at your production URL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating production admin: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating production admin user for NumWatch...")
    success = create_production_admin()
    sys.exit(0 if success else 1)