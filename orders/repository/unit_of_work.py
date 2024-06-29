from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class UnitOfWork:

    def __init__(self):
        """ Initialize the session factory object """
        self.engine = create_engine("sqlite:///orders.db")
        self.Session = sessionmaker(bind=self.engine)

    def __enter__(self):
        self.session = self.Session()
        return self

        # Return an instance of the unit of work object

    # Access to the exceptions raised during the context's creation in the exit
    def __exit__(self, exc_type, exc_val, traceback):
        # Check whether an exception took place
        if exc_type is not None:
            self.rollback() # Rollback the session
            self.session.close() # Close the database session
        self.session.close()

    def commit(self):
        """ Wrapper around SQLAlchemy's commit() method """
        self.session.commit()

    def rollback(self):
        """ Wrapper around SQLAlchemy's rollback() method """
        self.session.rollback()