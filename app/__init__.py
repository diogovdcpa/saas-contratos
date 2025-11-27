from flask import Flask, g, redirect, session, url_for

from app.settings import BASE_DIR, DATABASE_URL, SECRET_KEY
from app.db import SessionLocal, init_db


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "app" / "views"),
        static_folder=str(BASE_DIR / "public"),
        static_url_path="",
    )
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DATABASE_URL"] = DATABASE_URL

    init_db()

    @app.before_request
    def setup_request_state():
        g.db = SessionLocal()
        user_id = session.get("user_id")
        if user_id:
            from app.models.user import User

            g.user = g.db.get(User, user_id)
        else:
            g.user = None

    @app.teardown_request
    def teardown_request(exception=None):
        db_session = g.pop("db", None)
        if db_session is not None:
            db_session.close()
        SessionLocal.remove()

    @app.context_processor
    def inject_user():
        return {"current_user": getattr(g, "user", None)}

    @app.route("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("dashboard.home"))
        return redirect(url_for("auth.login"))

    from app.controllers.auth import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.contracts import contracts_bp
    from endpoints import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(api_bp)

    return app
