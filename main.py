from fasthtml.common import *
from pathlib import Path
from starlette.responses import Response, FileResponse
from starlette.staticfiles import StaticFiles
import mimetypes

app = FastHTML(
    # https://fastht.ml/docs/tutorials/by_example.html#styling-basics
    # Removido picolink pois a landing page usa Tailwind CSS
)

# Caminhos base
BASE_DIR = Path(__file__).parent
LANDING_PAGE_DIR = BASE_DIR / "levanta-dai-bora-treinar"
LANDING_PAGE_PATH = LANDING_PAGE_DIR / "index.html"
ASSETS_DIR = LANDING_PAGE_DIR / "assets"

# Caminhos para o site compilado do ecossistema
SITE_SYSTENTANDO_DIR = BASE_DIR / "site-systentando" / "dist"
SITE_SYSTENTANDO_PATH = SITE_SYSTENTANDO_DIR / "index.html"
SITE_ASSETS_DIR = SITE_SYSTENTANDO_DIR / "assets"

# Monta arquivos estáticos da pasta assets
try:
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
    # Monta arquivos estáticos do site compilado (React usa subpasta 'assets' no dist)
    if SITE_ASSETS_DIR.exists():
        app.mount("/site-assets", StaticFiles(directory=str(SITE_ASSETS_DIR)), name="site-assets")
except Exception as e:
    print(f"Aviso: Não foi possível montar arquivos estáticos: {e}")


# quando carregar a rota principal vamos criar umas regras para identificar o dominio de origem e carregar o contexto especifico
# se o dominio for *deacademias.com.br carregar a landing page levanta-dai
# se o dominio for *systentando.com.br/br carregar a landing page systentando

@app.route('/gymapp')
def serve_gymapp():
    """Carrega e serve o index.html da landing page LevantaDAI"""
    try:
        html_content = LANDING_PAGE_PATH.read_text(encoding='utf-8')
        return Response(content=html_content, media_type="text/html")
    except FileNotFoundError:
        return Div(
            H1("Erro: Arquivo não encontrado"),
            P(f"O arquivo {LANDING_PAGE_PATH} não foi encontrado."),
        )
    except Exception as e:
        return Div(H1("Erro ao carregar a landing page"), P(str(e)))

@app.route('/br')
def serve_systentando():
     """Serve o site compilado do Ecossistema Systentando"""
    try:
        if not SITE_SYSTENTANDO_PATH.exists():
            return Div(
                H1("Site não compilado"),
                P("O arquivo index.html não foi encontrado em dist/."),
                P("Execute 'npm run build' na pasta site-systentando primeiro.")
            )
        
        html_content = SITE_SYSTENTANDO_PATH.read_text(encoding='utf-8')
        
        # Ajuste técnico: Se o React index.html usa caminhos relativos como "/assets/...",
        # precisamos garantir que eles apontem para o mount correto "/site-assets/..."
        # ou que as rotas de assets sejam tratadas.
        html_content = html_content.replace('href="/assets/', 'href="/site-assets/')
        html_content = html_content.replace('src="/assets/', 'src="/site-assets/')
        
        return Response(content=html_content, media_type="text/html")
    except Exception as e:
        return Div(H1("Erro ao carregar ecossistema"), P(str(e)))

@app.route('/')
def get(req):
    """Router principal baseado no domínio (Host)"""
    host = req.headers.get("host", "").lower()
    
    # Lógica de roteamento por domínio
    if "deacademias.com.br" in host:
        return serve_gymapp()
    elif "systentando.com.br" in host:
        return serve_systentando()
    
    # Fallback para desenvolvimento local ou outros domínios
    return Div(
        H1("Systentando Hub"),
        P(f"Host identificado: {host}"),
        Ul(
            Li(A("Ver Landing Page (GymApp)", href="/gymapp")),
            Li(A("Ver Ecossistema (Systentando)", href="/br"))
        ),
        cls="container"
    )

@app.route('/favicon.ico')
def get_favicon():
    """Serve o favicon (retorna 404 se não existir)"""
    favicon_path = LANDING_PAGE_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(path=str(favicon_path), media_type="image/x-icon")
    return Response(content="", status_code=404)

# For a slightly more complex page, browse to "/example"
@app.route('/example')
def get():
    return (
        Title("Page Title"),
        Body(
            Header(
                H1(Nav(
                    Ul(Li(A("Home", href="/", style="color: inherit"))),
                    Ul(Li(A("Example", href="https://higheraspire.com", cls="secondary", target="_blank")))
                )),
            ),
            Main(
                H1("Congrats! 🎉"),
                P("You've built a website with FastHTML!"),
                P("Here are some helpful links:"),
                Ul(
                    Li(A("FastHTML Docs", href="https://fastht.ml/docs/")),
                    Li(
                        "FastHTML has an active ",
                        A("discord", href="https://discord.gg/qcXvcxMhdP"),
                        ". If you can't find an answer in the docs, try asking there.",
                    ),
                    Li(
                        "If you don't enjoy HTML/CSS, FastHTML integrates nicely with ",
                        A("picocss", href="https://picocss.com/"),
                        ", a small, simple, clean css framework. This page uses picocss. See ",
                        A("this page", href="https://4mrnhq.csb.app/"),
                        " for an example of what it can do.",
                    ),
                    Li(
                        "To connect to this railway app from CLI, install the ", A("railway CLI app", href="https://docs.railway.com/guides/cli#installing-the-cli"),
                        ", then run ",
                        Code("railway link"),
                    ),
                    Li(
                        "Many railway projects use docker, but I've found that FastHTML apps are simple enough that docker isn't strictly necessary. I would suggest using the python package and project manager ",
                        A("uv", href="https://docs.astral.sh/uv/"),
                        " (that is what this template is using)."
                    ),
                    Li(
                        "If this template helped you, please give the ", A("github repo", href="https://github.com/tristan-white/fh-railway-template/"),  " a ⭐ to help others find it!"
                    )
                )
            ),
            cls="container" # this centers the content on the within Body
        )
    )

@app.route('/my-page')
def get():
    return Div(
        P("Try creating a page here!")
    )

serve()