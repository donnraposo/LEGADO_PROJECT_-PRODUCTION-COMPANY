from rest_framework.exceptions import APIException


class ConflictError(APIException):
    status_code = 409
    default_detail = "O recurso foi alterado por outra operação."
    default_code = "conflict"
