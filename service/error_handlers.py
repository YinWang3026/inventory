# from flask import jsonify
from service.models import DataValidationError, DatabaseConnectionError
from service import app, status
from service.routes import api
from werkzeug.exceptions import NotFound, BadRequest, MethodNotAllowed, UnsupportedMediaType, InternalServerError

######################################################################
# Special API Registered Error Handlers
######################################################################

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE

@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@api.errorhandler(BadRequest)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message 
    }, status.HTTP_400_BAD_REQUEST
    
@api.errorhandler(NotFound)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return {
        'status': status.HTTP_404_NOT_FOUND, 
        'error': "Not Found", 
        'message': message
    }, status.HTTP_404_NOT_FOUND

@api.errorhandler(MethodNotAllowed)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return {
        'status': status.HTTP_405_METHOD_NOT_ALLOWED,
        'error': "Method not Allowed",
        'message': message,
    }, status.HTTP_405_METHOD_NOT_ALLOWED
        
@api.errorhandler(UnsupportedMediaType)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return {
        'status': status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        'error': "Unsupported media type",
        'message': message,
    }, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
 
@api.errorhandler(InternalServerError)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return {
        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'error': "Internal Server Error",
        'message': message
    }, status.HTTP_500_INTERNAL_SERVER_ERROR
