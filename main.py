from flask import Flask, render_template
from endpoints import api_bp


app = Flask(
    __name__,
    template_folder="view",
    static_folder="public",
    static_url_path="",
)


app.register_blueprint(api_bp)


@app.get("/")
def read_root():
    return render_template(
        "index.html",
        message="em breve saas para gerar contrato de prestaçao de serviço",
    )
