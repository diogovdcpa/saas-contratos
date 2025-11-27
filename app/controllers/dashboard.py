from flask import Blueprint, g, render_template, session

from app.controllers import login_required
from app.models.contract import Contract

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def home():
    user_id = session["user_id"]
    contracts = (
        g.db.query(Contract)
        .filter_by(user_id=user_id)
        .order_by(Contract.updated_at.desc())
        .all()
    )
    return render_template(
        "dashboard/index.html",
        contracts=contracts,
        total_contracts=len(contracts),
    )
