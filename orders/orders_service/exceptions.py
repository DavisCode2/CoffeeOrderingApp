class OrderNotFoundError(Exception):
    """Exception to signal that an order does not exist"""
    pass

class APIIntegrationError(Exception):
    """Exception to signal that an API integration error has taken place """
    pass

class InvalidActionError(Exception):
    """ Exception to signal that the action being performed is invalid """
    pass