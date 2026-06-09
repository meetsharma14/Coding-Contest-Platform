# ==================================
# PYDANTIC IMPORTS
# ==================================

# BaseModel → parent class for schemas
# EmailStr → validates email format
from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    Field
)

# Used for date and time fields
from datetime import datetime

# Used for optional values
from typing import Optional

from enum import Enum
import re


# ==================================
# USER SCHEMAS
# ==================================

# Input schema for user registration
class UserCreate(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$"
    )

    # Automatically validates email
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


# Input schema for login
class UserLogin(BaseModel):

    username: str

    password: str


# Response schema returned after
# user creation/login
class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    role: str

    created_at: datetime

    class Config:

        # Allows conversion from
        # SQLAlchemy objects
        from_attributes = True


# ==================================
# TOKEN SCHEMAS
# ==================================

# JWT response structure
class Token(BaseModel):

    access_token: str

    token_type: str


# Stores token payload data
class TokenData(BaseModel):

    username: Optional[str] = None


# ==================================
# PROBLEM SCHEMAS
# ==================================

# Input schema for creating
# a coding problem
ALLOWED_DIFFICULTIES = {
    "Easy", "Medium", "Hard"
}


class ProblemCreate(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=255
    )

    difficulty: str

    description: str = Field(
        min_length=1
    )

    sample_input: Optional[str] = None

    sample_output: Optional[str] = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(
        cls, v: str
    ) -> str:
        if v not in ALLOWED_DIFFICULTIES:
            raise ValueError(
                f"difficulty must be one of: "
                f"{', '.join(sorted(ALLOWED_DIFFICULTIES))}"
            )
        return v


# Output schema returned
# when fetching problems
class ProblemResponse(BaseModel):

    id: int

    title: str

    difficulty: str

    description: str

    sample_input: Optional[str] = None

    sample_output: Optional[str] = None

    class Config:

        # Converts SQLAlchemy object
        # into JSON response
        from_attributes = True


# ==================================
# CONTEST SCHEMAS
# ==================================

# Input schema for contest creation
class ContestCreate(BaseModel):

    title: str

    description: str

    start_time: datetime

    end_time: datetime


# Contest response schema
class ContestResponse(BaseModel):

    id: int

    title: str

    description: str

    start_time: datetime

    end_time: datetime

    is_active: bool

    class Config:

        from_attributes = True


# ==================================
# SUBMISSION SCHEMAS
# ==================================

# Input schema for solution submission
ALLOWED_LANGUAGES = {
    "python"
}


class SubmissionCreate(BaseModel):

    problem_id: int

    code: str = Field(
        min_length=1,
        max_length=50000
    )

    # Default language
    language: str = "python"

    @field_validator("language")
    @classmethod
    def validate_language(
        cls, v: str
    ) -> str:
        if v not in ALLOWED_LANGUAGES:
            raise ValueError(
                f"language must be one of: "
                f"{', '.join(sorted(ALLOWED_LANGUAGES))}"
            )
        return v


# Output schema for submissions
class SubmissionResponse(BaseModel):

    id: int

    user_id: int

    problem_id: int

    verdict: str

    score: int

    runtime_ms: int

    submitted_at: datetime

    class Config:

        from_attributes = True