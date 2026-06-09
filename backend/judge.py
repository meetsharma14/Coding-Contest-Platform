# ==================================
# IMPORT
# ==================================

# Used for calculating execution time
import time

# Logging for judge errors
import logging

logger = logging.getLogger(__name__)


# ==================================
# RUN PYTHON CODE
#
# Temporary online judge system
# Currently checks only compilation
#
# Future:
# Execute code inside Docker
# containers for security
# ==================================

def run_python_code(code: str, test_cases: list | None = None):

    """
    Temporary online judge.
    Later code will run safely
    inside Docker containers.
    """

    # Start timer before execution
    start = time.time()

    try:

        # ==================================
        # COMPILE USER CODE
        #
        # Checks syntax errors only
        #
        # Example:
        # def solve():
        #     print("Hello")
        #
        # Does NOT execute code
        # ==================================

        compile(
            code,
            "<submission>",
            "exec"
        )

        # ==================================
        # CALCULATE EXECUTION TIME
        # Convert seconds → milliseconds
        # ==================================

        runtime_ms = int(
            (time.time() - start) * 1000
        )

        # ==================================
        # SUCCESS RESPONSE
        # ==================================

        return {

            "verdict": "Accepted",

            "score": 100,

            "runtime_ms": runtime_ms
        }

    except SyntaxError as e:

        # ==================================
        # SYNTAX ERROR RESPONSE
        # ==================================

        return {

            "verdict": "Compilation Error",

            "score": 0,

            "runtime_ms": 0,

            "error": str(e)
        }

    except Exception as e:

        # ==================================
        # UNEXPECTED ERROR RESPONSE
        # Log for debugging
        # ==================================

        logger.error(
            "Unexpected judge error: %s", e
        )

        return {

            "verdict": "Judge Error",

            "score": 0,

            "runtime_ms": 0,

            "error": "Internal judge error"
        }
