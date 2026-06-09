# ==================================
# IMPORT
# ==================================

# Used for calculating execution time
import time


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

def run_python_code(
    code: str,
    test_cases: list | None = None
):

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
        # ERROR RESPONSE
        # If syntax/compilation fails
        # ==================================

        return {

            "verdict": "Compilation Error",

            "score": 0,

            "runtime_ms": 0,

            "error": str(e)
        }
