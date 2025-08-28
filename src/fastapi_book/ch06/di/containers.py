import sqlite3

from dependency_injector import containers, providers

from .services import AuthService, UserService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_connection = providers.Singleton(
        sqlite3.connect,
        database=config.db.database,
        check_same_thread=False,
    )

    user_service = providers.Factory(
        UserService,
        db_connection=db_connection,
    )

    auth_service = providers.Factory(
        AuthService,
        db_connection=db_connection,
    )