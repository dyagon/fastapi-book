from dependency_injector.wiring import inject, Provide


from .containers import Container
from .services import AuthService, UserService


@inject
def main(
    user_service: UserService = Provide[Container.user_service],
    auth_service: AuthService = Provide[Container.auth_service],
):
    user = user_service.get_user(user_id=1)
    print("User:", user)

    is_authenticated = auth_service.authenticate(username="alice", password="secret")
    print("Authenticated:", is_authenticated)

if __name__ == "__main__":
    container = Container()
    container.config.db.database.from_env("DB_PATH", default=":memory:")
    container.wire(modules=[__name__])

    # For demonstration, create a sample users table and insert a user
    db_conn = container.db_connection()
    cursor = db_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("alice", "secret"))
    db_conn.commit()

    main()