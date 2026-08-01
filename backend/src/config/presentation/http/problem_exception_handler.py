from uuid import uuid4

from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def problem_exception_handler(exc: Exception, context: dict[str, object]) -> Response | None:
    response = exception_handler(exc, context)
    if response is None:
        return None

    code = "REQUEST_FAILED"
    title = "Não foi possível concluir a solicitação"
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        code = "AUTHENTICATION_REQUIRED"
        title = "Autenticação necessária"
    elif isinstance(exc, ValidationError):
        code = "VALIDATION_ERROR"
        title = "Dados inválidos"

    response.data = {
        "type": f"https://legado.local/problems/{code.casefold().replace('_', '-')}",
        "title": title,
        "status": response.status_code,
        "code": code,
        "detail": "Revise a solicitação e tente novamente.",
        "trace_id": str(uuid4()),
    }
    response.content_type = "application/problem+json"
    return response
