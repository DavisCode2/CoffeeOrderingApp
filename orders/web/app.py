from pathlib import Path
import os

import yaml
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import (RequestResponseEndpoint, BaseHTTPMiddleware)
from jwt import (
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
)

from .api import auth

app = FastAPI(debug=True, openapi_url="/openapi/orders.json", docs_url="/docs/orders")

# Create the middleware class to inherit from starlette base class
class AuthorizeRequestMiddleware(BaseHTTPMiddleware):

    # Middleware entry point
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        # Do not authorize the request if AUTH_ON is false
        if os.getenv("AUTH_ON", "False") != "True":
        # If authorization is off, bind a default user named test to the request
            request.state.user_id = "test"
            # Pass the request to the path operations
            return await call_next(request)

        # The documentation endpoints should not be authorized
        if request.url.path in ["/docs/orders", "/openapi/orders.json"]:
            return await call_next(request)
        
        # According to specifications, Options should not be authorized
        if request.method == "OPTIONS":
            return await call_next(request)

        # Attempt to fetch the authorization header
        bearer_token = request.headers.get("Authorization")
        # If not set, return a 401 (Unauthorized) response
        if not bearer_token:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={
                "detail": "Missing access token",
                "body": "Missing access token",
            },)

        try:
            # Capture the token from the authorization header
            auth_token = bearer_token.split(" ")[1].strip()
            # Validate and retrieve the token's payload
            token_payload = auth.decode_and_validate_token(auth_token)
        # If the token is invalid, return a 401 (Unauthorize) response
        except(
            ExpiredSignatureError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            InvalidAudienceError,
            InvalidKeyError,
            InvalidSignatureError,
            InvalidTokenError,
            MissingRequiredClaimError,
        ) as error:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(error), "body": str(error)})

        else: 
            # extract the user_id from the token's subject field
            request.state.user_id = token_payload["sub"]

        return await call_next(request)

app.add_middleware(AuthorizeRequestMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oas_doc = yaml.safe_load((Path(__file__).parent / "../../orders.yaml").read_text())

app.openapi = lambda: oas_doc

from orders.web.api import api
