from datetime import datetime
from decimal import Decimal, InvalidOperation

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

UNITS = [
    "zero",
    "um",
    "dois",
    "três",
    "quatro",
    "cinco",
    "seis",
    "sete",
    "oito",
    "nove",
]
TEENS = {
    10: "dez",
    11: "onze",
    12: "doze",
    13: "treze",
    14: "quatorze",
    15: "quinze",
    16: "dezesseis",
    17: "dezessete",
    18: "dezoito",
    19: "dezenove",
}
TENS = {
    20: "vinte",
    30: "trinta",
    40: "quarenta",
    50: "cinquenta",
    60: "sessenta",
    70: "setenta",
    80: "oitenta",
    90: "noventa",
}
HUNDREDS = {
    1: "cento",
    2: "duzentos",
    3: "trezentos",
    4: "quatrocentos",
    5: "quinhentos",
    6: "seiscentos",
    7: "setecentos",
    8: "oitocentos",
    9: "novecentos",
}
SCALES = [
    (1, "mil", "mil"),
    (2, "milhão", "milhões"),
    (3, "bilhão", "bilhões"),
]


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


def _format_date_br(date_obj) -> str:
    return date_obj.strftime("%d/%m/%Y") if date_obj else "—"


def _format_currency_br(value: Decimal | None) -> str:
    amount = (value or Decimal("0")).quantize(Decimal("0.01"))
    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def _tres_digitos_por_extenso(n: int) -> str:
    if n == 0:
        return ""
    if n == 100:
        return "cem"

    centenas = n // 100
    dezenas_unidades = n % 100
    partes = []

    if centenas:
        partes.append(HUNDREDS[centenas])

    if dezenas_unidades:
        if dezenas_unidades < 10:
            partes.append(UNITS[dezenas_unidades])
        elif dezenas_unidades < 20:
            partes.append(TEENS[dezenas_unidades])
        else:
            dezenas = (dezenas_unidades // 10) * 10
            unidades = dezenas_unidades % 10
            if dezenas:
                partes.append(TENS[dezenas])
            if unidades:
                partes.append(UNITS[unidades])

    return " e ".join(partes)


def _numero_por_extenso(n: int) -> str:
    if n == 0:
        return "zero"

    grupos = []
    while n > 0:
        grupos.append(n % 1000)
        n //= 1000

    partes = []
    for idx, grupo in enumerate(grupos):
        if grupo == 0:
            continue
        grupo_texto = _tres_digitos_por_extenso(grupo)
        if idx == 0:
            partes.append(grupo_texto)
            continue

        escala = SCALES[idx - 1]
        singular, plural = escala[1], escala[2]

        if idx == 1 and grupo == 1:
            partes.append("mil")
        else:
            sufixo = singular if grupo == 1 else plural
            partes.append(f"{grupo_texto} {sufixo}")

    partes = partes[::-1]
    texto = ""
    for i, parte in enumerate(partes):
        if i > 0:
            sep = " e " if i == len(partes) - 1 else ", "
            texto += sep
        texto += parte
    return texto


def _valor_por_extenso(valor: Decimal | None) -> str:
    quantized = (valor or Decimal("0")).quantize(Decimal("0.01"))
    inteiro = int(quantized)
    centavos = int((quantized * 100) % 100)

    inteiro_ext = _numero_por_extenso(inteiro)
    moeda = "real" if inteiro == 1 else "reais"

    if centavos:
        centavos_ext = _numero_por_extenso(centavos)
        centavo_label = "centavo" if centavos == 1 else "centavos"
        return f"{inteiro_ext} {moeda} e {centavos_ext} {centavo_label}"

    return f"{inteiro_ext} {moeda}"


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
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", ln=True, align="C")

    pdf.set_font("Helvetica", size=11)
    pdf.ln(8)
    valor_formatado = _format_currency_br(contract.value)
    valor_extenso = _valor_por_extenso(contract.value)
    vencimento_formatado = _format_date_br(contract.due_date)
    pdf.multi_cell(
        0,
        7,
        "\n".join(
            [
                f"Título: {contract.title}",
                f"Contratante: {contract.client_name}",
                f"Contratado: {contract.provider_name}",
                f"Cidade: {contract.city}",
                f"Valor: {valor_formatado} ({valor_extenso})",
                f"Pagamento: {contract.payment_terms}",
                f"Vencimento: {vencimento_formatado}",
                f"Serviço: {contract.service_description}",
            ]
        ),
    )
    pdf.ln(4)

    def add_clause(title: str, body: str):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 7, body)
        pdf.ln(2)

    add_clause(
        "1. Objeto",
        "O presente contrato tem por objeto a prestação dos serviços acima descritos pelo CONTRATADO ao CONTRATANTE, conforme escopo, prazos e condições aqui estabelecidos.",
    )
    add_clause(
        "2. Vigência e Prazo",
        "Este contrato tem vigência a partir de sua assinatura. Quando aplicável, o vencimento indicado acima servirá como referência para conclusão, entrega ou renovação, salvo ajuste diferente entre as partes.",
    )
    add_clause(
        "3. Obrigações do Contratado",
        "Prestar os serviços com diligência e dentro do prazo; manter confidencialidade sobre informações do CONTRATANTE; informar eventuais impedimentos e solicitar materiais ou acessos necessários.",
    )
    add_clause(
        "4. Obrigações do Contratante",
        "Fornecer informações, materiais e acessos necessários; acompanhar entregas; efetuar os pagamentos nos prazos combinados; aprovar ou solicitar ajustes em tempo razoável.",
    )
    add_clause(
        "5. Pagamento",
        "O CONTRATANTE pagará ao CONTRATADO o valor ajustado, conforme a forma de pagamento indicada. Juros e correção poderão incidir em caso de atraso, conforme legislação aplicável.",
    )
    add_clause(
        "6. Propriedade Intelectual",
        "Salvo ajuste em contrário, entregas personalizadas pertencem ao CONTRATANTE após quitação. Ferramentas, métodos e know-how preexistentes permanecem de propriedade do CONTRATADO.",
    )
    add_clause(
        "7. Confidencialidade",
        "As partes manterão confidenciais quaisquer informações técnicas, comerciais ou estratégicas recebidas durante a execução deste contrato, pelo prazo de 5 anos após o término, salvo por obrigação legal.",
    )
    add_clause(
        "8. Rescisão",
        "O contrato pode ser rescindido por qualquer parte em caso de descumprimento material não sanado, ou por acordo mútuo. Valores devidos até a data da rescisão permanecem exigíveis.",
    )
    add_clause(
        "9. Responsabilidade",
        "O CONTRATADO responde pela execução dos serviços conforme boas práticas. Em nenhuma hipótese será responsável por danos indiretos, lucros cessantes ou perda de receita, salvo dolo.",
    )
    add_clause(
        "10. Foro",
        "As partes elegem o foro da cidade mencionada no cabeçalho para dirimir quaisquer dúvidas oriundas deste contrato, com renúncia a qualquer outro, por mais privilegiado que seja.",
    )

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Declaração e Assinaturas", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        0,
        7,
        "As partes declaram ter lido e concordado com as cláusulas acima. Este contrato pode ser assinado eletronicamente ou fisicamente em duas vias de igual teor.",
    )

    pdf.ln(14)
    pdf.cell(0, 7, f"Cidade: {contract.city}", ln=True)
    pdf.cell(
        0,
        7,
        f"Data: {vencimento_formatado if contract.due_date else '___/___/____'}",
        ln=True,
    )

    pdf.ln(18)
    pdf.cell(80, 7, "______________________________", ln=0)
    pdf.cell(30, 7, "", ln=0)
    pdf.cell(80, 7, "______________________________", ln=1)
    pdf.cell(80, 7, f"Contratante: {contract.client_name}", ln=0)
    pdf.cell(30, 7, "", ln=0)
    pdf.cell(80, 7, f"Contratado: {contract.provider_name}", ln=1)


    pdf_output = pdf.output(dest="S")
    pdf_bytes = pdf_output.encode("latin1") if isinstance(pdf_output, str) else bytes(
        pdf_output
    )
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'inline; filename="contrato_{contract.id}.pdf"'
    )
    return response
