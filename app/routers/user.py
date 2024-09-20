from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pony.orm import db_session, commit
from app.schemas import user as user_schema
from app.database.models import User, UserLog
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin,
    get_password_hash,
)

router = APIRouter()


@router.post("/register", response_model=user_schema.UserRegistrationResponse)
@db_session
def register(user: user_schema.UserCreate):
    if User.get(username=user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = get_password_hash(user.password)

    # Get the current local time
    current_time = datetime.now()

    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role, created_at=current_time)

    # Commit the transaction
    commit()


    # Convert to dictionary or use a schema to ensure all attributes are loaded before the session ends
    user_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
    }

    # Return the user data along with a success message
    return {
        "message": "User registration successful",
        "user": user_data
    }



@router.post("/login", response_model=user_schema.Token)
@db_session
def login(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get the current local time
        current_time = datetime.now()

        # Create a new UserLog entry
        UserLog(user=user, username=user.username, email=user.email, login_time=current_time)
        commit()

        access_token = create_access_token(data={"sub": user.username, "role": user.role})
        return {
            "message": "User login successful",
            "access_token": access_token,
            "token_type": "bearer"
        }


@router.put("/update/{user_id}", response_model=user_schema.User)
@db_session
def update_user(user_id: int, user_update: user_schema.UserUpdate, current_user: User = Depends(get_current_user)):
    db_user = User.get(id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Only the user or an admin can update the user
    if current_user.id != db_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    if user_update.username:
        db_user.username = user_update.username
    if user_update.email:
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)

    # Only admins can update the role
    if current_user.role == "admin" and user_update.role:
        db_user.role = user_update.role

    db_user.updated_at = datetime.utcnow()
    commit()
    return db_user


@router.get("/me", response_model=user_schema.User)
@db_session
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
