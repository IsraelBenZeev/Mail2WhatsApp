from fastapi import APIRouter
from fastapi import Request
from controllers.Users_Controller import get_users as get_users_controller

routerUsers = APIRouter()


@routerUsers.get("/get-users")
def get_users():
    return get_users_controller()
