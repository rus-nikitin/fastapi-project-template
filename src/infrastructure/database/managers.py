from typing import Protocol, TYPE_CHECKING
import logging


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


logger = logging.getLogger(__name__)


class BaseDbManager(Protocol):
    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    def get_db_provider(self) -> 'AsyncSession | AsyncIOMotorDatabase | None':
        ...

    def get_provider_type(self) -> str:
        ...


class NoOpDbManager(BaseDbManager):
    """No-operation database manager when no database is needed"""

    def __init__(self, **config):
        pass

    async def connect(self) -> None:
        logger.info("No database configured - skipping connection")

    async def disconnect(self) -> None:
        logger.info("No database configured - skipping disconnection")

    def get_db_provider(self) -> None:
        raise RuntimeError("No database manager configured. Remove database dependencies from endpoints.")

    def get_provider_type(self) -> str:
        return "none"


class SQLAlchemyDbManager(BaseDbManager):
    """SQLAlchemy connection manager"""

    def __init__(self, **config):
        self.database_uri = config.get("database_uri")
        self.engine: 'AsyncEngine | None' = None
        self.session_factory: 'async_sessionmaker | None' = None


    async def connect(self) -> None:
        if self.engine is None:
            try:
                from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
                self.engine = create_async_engine(self.database_uri)  # TODO add Excepion
                self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
                logger.info(f"Connected to SQL database: {self.database_uri}")
            except ImportError as e:
                raise RuntimeError(
                    "SQLAlchemy is required for SQL database support. "
                    "Install it with: pip install 'sqlalchemy[asyncio]'"
                ) from e

    async def disconnect(self) -> None:
        """Close database engine"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
            logger.info("SQL database connection closed")


    def get_db_provider(self) -> 'AsyncSession':
        """Get async session factory"""
        if self.session_factory is None:
            raise RuntimeError("SQL database not connected. Call connect() first.")
        return self.session_factory()


    def get_provider_type(self) -> str:
        return "sql"


class MotorDbManager(BaseDbManager):
    """MongoDB connection manager"""

    def __init__(self, **config):
        self.mongo_dsn = str(config.get("mongo_dsn"))
        self.mongo_db_name = config.get("mongo_db_name")
        self.client: 'AsyncIOMotorClient | None' = None
        self.database: 'AsyncIOMotorDatabase | None'  = None


    async def connect(self) -> None:
        """Create MongoDB connection"""
        if self.client is None:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                self.client = AsyncIOMotorClient(self.mongo_dsn)
                self.database = self.client.get_database(self.mongo_db_name)
                logger.info(f"Connected to MongoDB database: {self.mongo_db_name}")
            except ImportError as e:
                raise RuntimeError(
                    "AsyncIOMotorClient is required for MongoDB database support. "
                    "Install it with: pip install 'motor'"
                ) from e


    async def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("MongoDB database connection closed")


    def get_db_provider(self) -> 'AsyncIOMotorDatabase':
        if self.database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.database


    def get_provider_type(self) -> str:
        return "mongodb"


class DbManagerFactory:
    _managers = {
        "sqlalchemy": SQLAlchemyDbManager,
        "motor": MotorDbManager,
        "none": NoOpDbManager
    }

    @classmethod
    def create_manager(cls, **config) -> BaseDbManager:
        db_type = config.get("db_type")

        # If no database manager specified, use no-op manager
        if db_type is None:
            logger.info("No database manager specified, using no-op manager")
            return cls._managers["none"]()

        if db_type not in cls._managers:
            available = ", ".join(cls._managers.keys())
            raise ValueError(f"Unknown database manager: {db_type}. Available: {available}")

        logger.info(f"Creating database manager: {db_type}")
        return cls._managers[db_type](**config)
