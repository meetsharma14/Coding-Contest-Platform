# ==================================
# IMPORTS
# ==================================

# FastAPI utilities
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

# Database session
from sqlalchemy.orm import Session

# Database connection dependency
from database import get_db

# Database models
from models import Problem, User

# Pydantic schemas
from schemas import (
    ProblemCreate,
    ProblemResponse
)

# Authentication and role checks
from auth import (
    get_current_user,
    get_admin_user
)

# Shared CRUD utilities
from crud import (
    get_or_404,
    save_and_refresh,
    check_unique_or_400
)


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base endpoint path
    prefix="/problems",

    # Group name in Swagger UI
    tags=["Problems"]
)


# ==================================
# CREATE PROBLEM
# ==================================

@router.post(
    "/",

    # Response schema
    response_model=ProblemResponse,

    # Return status code
    status_code=status.HTTP_201_CREATED
)
def create_problem(

    # Request body data
    problem: ProblemCreate,

    # Database dependency
    db: Session = Depends(get_db),

    # Enable this later if only admin can create
    # admin: User = Depends(get_admin_user)
):

    # Check whether problem already exists
    check_unique_or_400(
        db, Problem,
        Problem.title, problem.title,
        "Problem already exists"
    )

    # Create new database object
    new_problem = Problem(

        title=problem.title,

        difficulty=problem.difficulty,

        description=problem.description,

        sample_input=
            problem.sample_input,

        sample_output=
            problem.sample_output
    )

    # Save and return
    return save_and_refresh(
        db, new_problem
    )


# ==================================
# GET ALL PROBLEMS
# ==================================

@router.get(
    "/",

    response_model=
    list[ProblemResponse]
)
def get_problems(

    # Optional difficulty filter
    difficulty: str | None = Query(
        default=None
    ),

    db: Session = Depends(
        get_db
    )
):

    # Select all problems
    query = db.query(
        Problem
    )

    # Apply difficulty filter
    if difficulty:

        query = query.filter(

            Problem.difficulty
            == difficulty
        )

    # Fetch data
    problems = query.all()

    return problems


# ==================================
# GET SINGLE PROBLEM
# ==================================

@router.get(

    "/{problem_id}",

    response_model=
    ProblemResponse
)
def get_problem(

    problem_id: int,

    db: Session = Depends(
        get_db
    )
):

    return get_or_404(
        db, Problem, problem_id,
        "Problem not found"
    )


# ==================================
# DELETE PROBLEM
# ==================================

@router.delete(
    "/{problem_id}"
)
def delete_problem(

    problem_id: int,

    db: Session = Depends(
        get_db
    ),

    # Only admin can delete
    admin: User = Depends(
        get_admin_user
    )
):

    # Find problem
    problem = get_or_404(
        db, Problem, problem_id,
        "Problem not found"
    )

    # Remove from database
    db.delete(
        problem
    )

    db.commit()

    return {

        "message":
        "Problem deleted successfully"
    }


# ==================================
# USER ACCESS TEST
# ==================================

@router.get(
    "/me/test"
)
def test_user_access(

    # Verify JWT token
    current_user: User = Depends(
        get_current_user
    )
):

    return {

        "message":
        f"Welcome {current_user.username}",

        "role":
        current_user.role
    }
