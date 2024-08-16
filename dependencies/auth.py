from fastapi import Request
from repository.aggregates import stats_user_type
import json
from handler_exception import SameUsernamePasswordException


# def count_user_by_type(request: Request):
#     try:
#         count = stats_user_type[request.query_params.get("type")]
#         count += 1
#         stats_user_type[request.query_params.get("type")] = count
#         with open("stats_user_type.txt", "w") as file:
#             file.write(json.dumps(stats_user_type))
#     except KeyError:
#         stats_user_type[request.query_params.get("type")] = 1
#         with open("stats_user_type.txt", "w") as file:
#             file.write(json.dumps(stats_user_type))

def check_credential_error(request: Request):
    username = request.query_params.get("uname")
    password = request.query_params.get("passwd")
    if username and password and username == password:
        raise SameUsernamePasswordException()
