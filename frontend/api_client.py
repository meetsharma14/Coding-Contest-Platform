# ==================================
# SHARED API CLIENT
#
# Reusable HTTP helpers for the
# Streamlit frontend
# ==================================

import streamlit as st
import requests

API_BASE_URL = "https://coding-contest-platform-gv03.onrender.com/"


def _headers():
    """Return auth headers if a token is stored in session state."""

    if st.session_state.get("token"):
        return {
            "Authorization":
                f"Bearer {st.session_state.token}"
        }

    return {}


def api_get(path: str):
    """Perform a GET request and return the Response object."""

    return requests.get(
        f"{API_BASE_URL}{path}",
        headers=_headers()
    )


def api_post(path: str, payload: dict):
    """Perform a POST request with a JSON body and return the Response object."""

    return requests.post(
        f"{API_BASE_URL}{path}",
        json=payload,
        headers=_headers()
    )
