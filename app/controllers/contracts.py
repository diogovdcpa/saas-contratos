from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO

from fpdf import FPDF
from flask import (
    Blueprint,
    abort,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.controllers import login_required
from app.models.contract import Contract

contracts_bp = Blueprint("contracts", __name__, url_prefix="/contratos")


def _parse_decimal(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        cleaned = value.replace(",", ".")
        return Decimal(cleaned)
    except (InvalidOperation, AttributeError):
        return None


def _parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _get_contract_or_404(contract_id: int) -> Contract:
    user_id = session.get("user_id")
    contract = (
        g.db.query(Contract)
        .filter(Contract.id == contract_id, Contract.user_id == user_id)
        .first()
    )
    if not contract:
        abort(404)
    return contract


@contracts_bp.route("/")
@login_required
def list_contracts():
    user_id = session["user_id"]
    contracts = (
        g.db.query(Contract)
        .filter_by(user_id=user_id)
        .order_by(Contract.updated_at.desc())
        .all()
    )
    return render_template("contratos/lista.html", contracts=contracts)


@contracts_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create_contract():
    if request.method == "POST":
        form = request.form
        title = (form.get("title") or "").strip()
        provider_name = (form.get("provider_name") or "").strip()
        client_name = (form.get("client_name") or "").strip()
        service_description = (form.get("service_description") or "").strip()
        value = _parse_decimal(form.get("value") or "")
        payment_terms = (form.get("payment_terms") or "").strip()
        city = (form.get("city") or "").strip()
        due_date = _parse_date(form.get("due_date") or "")
        status = (form.get("status") or "rascunho").strip() or "rascunho"

        errors = []
        required_fields = [
            (title, "Título é obrigatório."),
            (provider_name, "Contratado é obrigatório."),
            (client_name, "Contratante é obrigatório."),
            (service_description, "Serviço é obrigatório."),
            (value, "Valor é obrigatório."),
            (payment_terms, "Forma de pagamento é obrigatória."),
            (city, "Cidade é obrigatória."),
        ]
        for field_value, message in required_fields:
            if not field_value:
                errors.append(message)

        if form.get("due_date") and not due_date:
            errors.append("Data inválida. Use o formato AAAA-MM-DD.")

        if errors:
            for err in errors:
                flash(err, "error")
        else:
            contract = Contract(
                title=title,
                provider_name=provider_name,
                client_name=client_name,
                service_description=service_description,
                value=value,
                payment_terms=payment_terms,
                city=city,
                status=status,
                due_date=due_date,
                user_id=session["user_id"],
            )
            g.db.add(contract)
            g.db.commit()
            flash("Contrato criado com sucesso.", "success")
            return redirect(url_for("contracts.list_contracts"))

    return render_template("contratos/form.html", contract=None)


@contracts_bp.route("/<int:contract_id>/editar", methods=["GET", "POST"])
@login_required
def edit_contract(contract_id: int):
    contract = _get_contract_or_404(contract_id)

    if request.method == "POST":
        form = request.form
        contract.title = (form.get("title") or "").strip()
        contract.provider_name = (form.get("provider_name") or "").strip()
        contract.client_name = (form.get("client_name") or "").strip()
        contract.service_description = (form.get("service_description") or "").strip()
        value = _parse_decimal(form.get("value") or "")
        contract.payment_terms = (form.get("payment_terms") or "").strip()
        contract.city = (form.get("city") or "").strip()
        contract.status = (form.get("status") or "rascunho").strip() or "rascunho"
        contract.due_date = _parse_date(form.get("due_date") or "")

        errors = []
        if value is None:
            errors.append("Valor é obrigatório.")
        else:
            contract.value = value

        required_pairs = [
            (contract.title, "Título é obrigatório."),
            (contract.provider_name, "Contratado é obrigatório."),
            (contract.client_name, "Contratante é obrigatório."),
            (contract.service_description, "Serviço é obrigatório."),
            (contract.payment_terms, "Forma de pagamento é obrigatória."),
            (contract.city, "Cidade é obrigatória."),
        ]
        for val, message in required_pairs:
            if not val:
                errors.append(message)

        if request.form.get("due_date") and contract.due_date is None:
            errors.append("Data inválida. Use o formato AAAA-MM-DD.")

        if errors:
            for err in errors:
                flash(err, "error")
        else:
            g.db.commit()
            flash("Contrato atualizado.", "success")
            return redirect(url_for("contracts.list_contracts"))

    return render_template("contratos/form.html", contract=contract)


@contracts_bp.route("/<int:contract_id>/excluir", methods=["POST"])
@login_required
def delete_contract(contract_id: int):
    contract = _get_contract_or_404(contract_id)
    g.db.delete(contract)
    g.db.commit()
    flash("Contrato excluído.", "info")
    return redirect(url_for("contracts.list_contracts"))


@contracts_bp.route("/<int:contract_id>/pdf")
@login_required
def contract_pdf(contract_id: int):
    contract = _get_contract_or_404(contract_id)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Contrato de Prestação de Serviço", ln=True, align="C")

    pdf.set_font("Helvetica", size=12)
    pdf.ln(8)
    rows = [
        ("Título", contract.title),
        ("Contratante", contract.client_name),
        ("Contratado", contract.provider_name),
        ("Serviço", contract.service_description),
        ("Valor", f"R$ {contract.value:.2f}"),
        ("Pagamento", contract.payment_terms),
        ("Cidade", contract.city),
        ("Status", contract.status),
        ("Vencimento", contract.due_date.isoformat() if contract.due_date else "-"),
    ]
    for label, value in rows:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(40, 8, f"{label}:", ln=0)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 8, str(value))
        pdf.ln(1)

    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0,
        8,
        "Gerado automaticamente. Revise o texto antes de assinar.",
        align="C",
    )

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'inline; filename="contrato_{contract.id}.pdf"'
    )
    return response
