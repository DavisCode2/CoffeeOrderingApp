from orders.orders_service.orders import Order
from orders.repository import models


class OrdersRepository:
    def __init__(self, session):
        # session object for the repository initializer method.
        self.session = session

    def add(self, items, user_id):
        record = OrderModel(
            # Create a record for each order item while recording the order
            items=[models.OrderItemModel(**item) for item in items]
        )
        # Add the record to the session object
        self.session.add(record)
        # Return an instance of order class
        return Order(**record.dict(), order_=record)

    def _get(self, id_, **filters):
        # Method to retrieve order by id
        return {
            # Fetch the record using SQLAlchemy's first() method
            self.session.query(models.OrderModel).filter(models.OrderModel.id == str(id_)).filter(**filters).first()
        }
    
    def get(self, id_, **filters):
        # Retrieve an order using the method above
        order = self._get(id_, **filters)
        if order is not None:
            # if the order exists, we return an Order object
            return Order(**order.dict())

    def list(self, limit=None, **filters):
        # Accepts a limit parameter and optional filters
        query = self.session.query(models.OrderModel)
        # Filter to see if order is cancelled
        if 'cancelled' in filters:
            cancelled = filters.pop('cancelled')
            if cancelled:
                query = query.filter(models.OrderModel.status == 'cancelled')
            
            else: 
                query = query.filter(models.OrderModel != 'cancelled')

        records = query.filter_by(**filters).limit(limit).all()
        # Return a list of Order objects
        return [Order(**record.dict()) for record in records]

    
    def update(self, id_, **payload):
        record = self._get(id_)
        if 'items' in payload:
            # To update an order, delete the items linked to the order
            for item in record.items:
                self.session.delete(item)
            record.items = [models.OrderItemModel(**item) for item in payload.pop('items')]
        
        # Update the database object using setattr() funtion
        for key, value in payload.items():
            setattr(record, key, value)
        
        return Order(**record.dict())

    
    def delete(self, id_):
        self.session.delete(self._get(id_))