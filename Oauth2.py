from fastapi import Depends, FastAPI, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from typing import Annotated
from schmas import *
from jwtToken import verifyjwttoken


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verifyjwttoken(token , credentials_exception)