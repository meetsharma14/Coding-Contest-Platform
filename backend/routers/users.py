# ==================================
# IMPORTS
# ==================================

# FastAPI utilities
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

# Database session
from sqlalchemy.orm import Session

# Database error handling
from sqlalchemy.exc import IntegrityError

# Logging
import logging

logger = logging.getLogger(__name__)

# Database connection dependency
from database import get_db

# Database model
from models import User

# Pydantic schemas
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token
)

# Authentication utilities
from auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user
)


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base endpoint URL
    prefix="/users",

    # Group name in Swagger UI
    tags=["Users"]
)


# ==================================
# USER REGISTRATION
# ==================================

@router.post(

    "/register",

    # Expected response schema
    response_model=UserResponse
)
def register(

    # Request body
    user: UserCreate,

    # Database dependency
    db: Session = Depends(get_db)
):

    # Check if username exists
    existing_username = (

        db.query(User)

        .filter(
            User.username
            == user.username
        )

        .first()
    )

    if existing_username:

        raise HTTPException(

            status_code=400,

            detail=
            "Username already exists"
        )

    # Check if email exists
    existing_email = (

        db.query(User)

        .filter(
            User.email
            == user.email
        )

        .first()
    )

    if existing_email:

        raise HTTPException(

            status_code=400,

            detail=
            "Email already exists"
        )

    # Create new user object
    new_user = User(

        username=
            user.username,

        email=
            user.email,

        # Store hashed password
        password_hash=
            hash_password(
                user.password
            ),

        role=
            "participant"
    )

    # Add to database session
    db.add(
        new_user
    )

    try:

        # Save data
        db.commit()

        # Refresh object and get generated fields
        db.refresh(
            new_user
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    except Exception as e:

        db.rollback()
        logger.error("Registration failed: %s", e)

        raise HTTPException(
            status_code=500,
            detail="Registration failed due to a server error"
        )

    return new_user


# ==================================
# USER LOGIN
# ==================================

@router.post(

    "/login",

    response_model=Token
)
def login(

    credentials: UserLogin,

    db: Session = Depends(
        get_db
    )
):

    # Authenticate user
    user = authenticate_user(

        credentials.username,

        credentials.password,

        db
    )

    # Invalid credentials
    if not user:

        raise HTTPException(

            status_code=
            status.HTTP_401_UNAUTHORIZED,

            detail=
            "Invalid username or password"
        )

    # Generate JWT token
    access_token = create_access_token(

        data={

            # Subject field
            "sub":
            user.username
        }
    )

    return {

        "access_token":
            access_token,

        "token_type":
            "bearer"
    }


# ==================================
# CURRENT USER PROFILE
# ==================================

@router.get(

    "/me",

    response_model=
    UserResponse
)
def get_profile(

    # Verify logged-in user
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user