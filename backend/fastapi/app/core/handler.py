import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from .exception import AppException

logger = logging.getLogger("app")


def global_exception_handler(request: Request, exception: AppException):
  return JSONResponse(
    status_code=exception.status_code,
    content={
      "error": exception.error_code,
      "detail": exception.message
    }
  )


def generic_exception_handler(request: Request, exception: Exception):
  logger.error(f"Unhandled exception error: {exception}", exc_info=True)
  return JSONResponse(
    status_code=500,
    content={
      "error": "INTERNAL_SERVER_ERROR",
      "details": "Error: An unexpected error occured on server"
    }
  )
