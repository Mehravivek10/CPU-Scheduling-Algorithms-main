from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import subprocess
import shutil
import os
from typing import List

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))
BINARY_PATH = os.path.join(PROJECT_ROOT, "lab4")

app = FastAPI(title="CPU Scheduling Visualizer")
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "static")), name="static")

templates_env = Environment(
    loader=FileSystemLoader(ROOT_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

def ensure_built_binary() -> None:
    if not os.path.exists(BINARY_PATH):
        # Attempt to build using make
        try:
            subprocess.run(["make", "-C", PROJECT_ROOT, "all"], check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Failed to build C++ binary: {exc}")


def run_simulation_json(operation: str, algos: str, last_instant: int, processes: List[str]) -> str:
    ensure_built_binary()
    if operation != "json":
        raise ValueError("operation must be 'json'")
    input_lines = [f"{operation} {algos} {last_instant} {len(processes)}"] + processes
    input_payload = "\n".join(input_lines) + "\n"

    try:
        proc = subprocess.run(
            [BINARY_PATH],
            input=input_payload.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Simulation failed: {exc.stderr.decode()}")

    return proc.stdout.decode()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = templates_env.get_template("index.html")
    html = template.render()
    return HTMLResponse(content=html)


@app.post("/api/run")
async def api_run(payload: dict):
    try:
        algos = payload.get("algos", "1,2-4,3")
        last_instant = int(payload.get("lastInstant", 20))
        processes = payload.get("processes", ["P1,0,3", "P2,2,5", "P3,3,2"]) 
        if not isinstance(processes, list):
            raise ValueError("processes must be a list of strings like 'P1,0,3'")
        output = run_simulation_json("json", algos, last_instant, processes)
        return Response(content=output, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))