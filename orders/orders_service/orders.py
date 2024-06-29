import requests
from orders.orders_service.exceptions import (APIIntegrationError, InvalidActionError)


class OrderItem:
    """ Business object that represent an order item """
    def __init__(self, id, product, quantity, size):
        self.id = id
        self.product = product
        self.quantity = quantity
        self.size = size


class Order: 
    """ for the order service """
    def __init__(self, id, created, items, status, schedule_id=None, delivery_id=None, order_ = None):
        # the order parameter represents a database model instance
        self._id = id
        self._created = created
        # An OrderItem object for each order item 
        self.items = [OrderItem(**item) for item in items]
        self._status = status
        self.schedule_id = schedule_id
        self.delivery_id = delivery_id

    # resolve the id dynamically by using property() decorator
    @property
    def id(self):
        return self._id or self._order.id

    @property
    def created(self):
        return self._created or self._order.created

    @property
    def status(self):
        return self._status or self._order.status


    def cancel(self):
        """Method to call for cancelling an order"""
        if self.status== 'progress': 
        # If an order is in progress, we cancel its schedule bycalling the kitchen API.
            kitchen_base_url = "http://localhost:3000/kitchen"
            response = requests.post(f"{kitchen_base_url}/schedules/{self.schedule_id}/cancel", json={"order": [item.dict() for item in self.items]},)

            if response.status_code == 200:
                # if response is successful, return 
                return 
            # if not, raise an APIIntegrationError
            raise APIIntegrationError(f"Could not cancel order with id {self.id}")
        
        if self.status == "delivery":
        # do not allow orders that are being delivered to be cancelled
            raise InvalidActionError(f"Cannot cancel order with id {self.id}")

    
    def pay(self): 
        """ Process the payment by calling the payment API """
        response = requests.post("http://localhost:3001/payments", json={'order_id': self.id})

        if response.status_code == 201:
            return
        
        raise APIIntegrationError(f"Could not process payment  for order with id {self.id}")    

    
    def schedule(self):
        """ Schedule an order for production by calling the kitchen API """

        response = requests.post("http://localhost:3000/kitchen/schedules", json={"order": [item.dict() for item in self.items]})

        if response.status_code == 201:
            # If the response from the kitchen service is successful, we return the schedule ID.
            return response.json()['id']

        raise APIIntegrationError(f"Could not schedule order with id {self.id}")