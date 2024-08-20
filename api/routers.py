from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from tarantool import error

from database import tt_connect
from models import LoginRequest, User
from auth import create_access_token, authenticate_user, get_current_user

router = APIRouter(prefix='/api')


test_user = {
    'admin': {
        'username': 'admin',
        'hashed_password': '$2b$12$AtZJO38RdVRpUS1/fJGrdOSXdXLloYKKtTFAb3SkV/BWQIh47XE.m'
    }
}


@router.post('/login')
async def get_access_token(request_data: Annotated[LoginRequest, Depends()]) -> dict:
    user = authenticate_user(request_data.username, request_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )
    access_token = create_access_token(data={'sub': user.username})

    return {'token': access_token}


@router.post('/write')
async def write_values(current_user: Annotated[User, Depends(get_current_user)],
                       data: dict[int, str], space: str):
    errors = {}
    ok = {}
    data_pairs = data.items()
    if len(data_pairs) == 0:
        return {'status': 'success',
                'info': 'No data to write'}
    if len(data.keys()) != len(set(data.keys())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Duplicate keys are in request'
        )
    for kv in data_pairs:
        try:
            db_connection = tt_connect()
            db_connection.insert(space_name=space, values=kv)
            ok[kv[0]] = 'successfully written'
        except error.SchemaError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'There is no space with name {space}'
            )
        except error.NetworkError:
            return {'status': 'error',
                    'info': 'Can not reach database'}
        except error.DatabaseError:
            errors[kv[0]] = 'Key already exists'
            continue
    if len(errors) != 0 and len(ok) != 0:
        return {'status': 'partial success',
                'info': 'key(s) already exists',
                'duplicated keys': errors,
                'success': ok}
    elif len(errors) != 0 and len(ok) == 0:
        return {'status': 'error',
                'info': 'key(s) already exists',
                'duplicated keys': errors}
    else:
        return {'status': 'success'}


@router.post('/read')
async def get_values(current_user: Annotated[User, Depends(get_current_user)],
                     request: dict[str, list[int]], space: str) -> dict:
    data = {}
    empty = {}
    for key in request['keys']:
        try:
            db_connection = tt_connect()
            selected = db_connection.select(space_name=space, key=key)
        except error.SchemaError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'There is no space with name {space}'
            )
        except error.NetworkError:
            return {'status': 'error',
                    'info': 'Can not reach database'}
        except error.DatabaseError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Bad request. Only positive integers allowed'
            )
        if len(selected) != 0:
            data[key] = selected[0][1]
        elif len(selected) == 0:
            empty[key] = 'No such key in database'

    print(empty)
    if len(empty) != 0:
        return {'status': 'partial success',
                'info': 'missing keys are in request',
                'missing keys': empty,
                'data': data}
    else:
        return {'status': 'success',
                'data': data}
