from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        errors = []

        if not email:
            errors.append("Email é obrigatório.")
        if not password:
            errors.append("Senha é obrigatória.")

        if not errors:
            user = g.db.query(User).filter_by(email=email).first()
            if not user or not user.check_password(password):
                errors.append("Credenciais inválidas.")
            else:
                session["user_id"] = user.id
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("dashboard.home"))

        for err in errors:
            flash(err, "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        errors = []

        if not name:
            errors.append("Nome é obrigatório.")
        if not email:
            errors.append("Email é obrigatório.")
        if not password:
            errors.append("Senha é obrigatória.")

        if not errors:
            existing = g.db.query(User).filter_by(email=email).first()
            if existing:
                errors.append("Email já cadastrado.")

        if errors:
            for err in errors:
                flash(err, "error")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            g.db.add(user)
            g.db.commit()
            session["user_id"] = user.id
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("dashboard.home"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
