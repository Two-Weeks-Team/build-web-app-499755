from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import init_db, seed_demo_data
from routes import router


app = FastAPI(title="FormulateFit AI Backend", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_demo_data()



@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset='UTF-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1.0' />
        <title>FormulateFit AI Backend</title>
      </head>
      <body style="margin:0;background:#0f1115;color:#e8edf2;font-family:Inter,Arial,sans-serif;">
        <div style="max-width:900px;margin:40px auto;padding:24px;line-height:1.6;">
          <h1 style="margin:0 0 12px 0;color:#7dd3fc;">FormulateFit AI Backend</h1>
          <p style="color:#b6c2cf;">Turn messy fitness goals into a structured, editable training blueprint in one pass.</p>

          <h2>Core Endpoints</h2>
          <ul>
            <li><strong>GET</strong> /health</li>
            <li><strong>POST</strong> /plan and /api/plan</li>
            <li><strong>POST</strong> /insights and /api/insights</li>
            <li><strong>GET</strong> /blueprints and /api/blueprints</li>
            <li><strong>POST</strong> /blueprints/save and /api/blueprints/save</li>
          </ul>

          <h2>Tech Stack</h2>
          <p>FastAPI 0.115.0 · SQLAlchemy 2.0.35 · Pydantic 2.9.0 · httpx 0.27.0 · PostgreSQL-ready via psycopg 3.2.3 · DigitalOcean Serverless Inference (anthropic-claude-4.6-sonnet)</p>

          <p>
            <a href='/docs' style='color:#7dd3fc;'>Swagger Docs</a>
            &nbsp;|&nbsp;
            <a href='/redoc' style='color:#7dd3fc;'>ReDoc</a>
          </p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
