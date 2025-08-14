from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create Base before importing models to avoid circular import
Base = declarative_base()

class SQLiteDatabase:
    def __init__(self, db_path='ecommerce.db'):
        """
        Initialize SQLite database connection
        
        :param db_path: Path to SQLite database file
        """
        # Use in-memory database with StaticPool for thread safety
        self.engine = create_engine(
            f'sqlite:///{db_path}', 
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """
        Get a new database session
        
        :return: SQLAlchemy session
        """
        return self.Session()

    def create_all_tables(self):
        """
        Create all tables defined in Base
        """
        Base.metadata.create_all(self.engine)

    def drop_all_tables(self):
        """
        Drop all tables defined in Base
        """
        Base.metadata.drop_all(self.engine)

# Global database instance
db = SQLiteDatabase()
