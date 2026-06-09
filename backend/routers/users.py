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

# Shared CRUD utilities
from crud import (
    save_and_refresh,
    check_unique_or_400
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
    check_unique_or_400(
        db, User,
        User.username, user.username,
        "Username already exists"
    )

    # Check if email exists
    check_unique_or_400(
        db, User,
        User.email, user.email,
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

    # Save and return
    return save_and_refresh(
        db, new_user
    )


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
