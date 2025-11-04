#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import click
import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(__file__)
ENV_FILE = os.path.join(ROOT, ".env")
ENV_EXAMPLE = os.path.join(ROOT, ".env.example")
DOCKER_COMPOSE = os.environ.get("DOCKER_COMPOSE", "docker-compose")


def run(cmd, check=True):
    proc = subprocess.run(cmd, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    click.echo(proc.stdout)
    if check and proc.returncode != 0:
        raise click.ClickException(f"Command {' '.join(cmd)} failed")
    return proc


def ensure_env():
    if not os.path.exists(ENV_FILE):
        raise click.ClickException(
            ".env not found. Run `./devup.py init` first.")
    load_dotenv(ENV_FILE)

# ---------------- CLI ----------------


@click.group()
def cli():
    """DevUp — automate local onboarding environment."""
    pass


@cli.command()
def init():
    """Create .env from .env.example."""
    if not os.path.exists(ENV_EXAMPLE):
        raise click.ClickException(".env.example missing.")
    if os.path.exists(ENV_FILE):
        if not click.confirm(".env exists. Overwrite?"):
            click.echo("Aborted.")
            return
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    click.echo(click.style("✅ Created .env from template", fg="green"))


@cli.command()
@click.option("--detach/--no-detach", default=True, help="Run in background")
def up(detach):
    """Start docker-compose stack."""
    cmd = [DOCKER_COMPOSE, "up"]
    if detach:
        cmd.append("-d")
    run(cmd)
    click.echo(click.style("🚀 Environment starting...", fg="cyan"))


@cli.command()
def status():
    """Show container status and health."""
    ensure_env()
    run([DOCKER_COMPOSE, "ps"], check=False)

    # --- Mock API status ---
    api_port = os.getenv("MOCK_API_PORT", "6000")
    try:
        r = requests.get(f"http://localhost:{api_port}/health", timeout=3)
        if r.ok:
            click.echo(click.style("✅ mock_api healthy", fg="green"))
        else:
            click.echo(click.style("⚠ mock_api unhealthy", fg="yellow"))
    except requests.RequestException:
        click.echo(click.style("❌ mock_api unreachable", fg="red"))

    # --- MySQL status ---
    click.echo("Attempting mysql ping via docker-compose exec")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST", "localhost")

    mysql_cmd = [
        DOCKER_COMPOSE, "exec", "-T", "mysql",
        "mysqladmin", "ping",
        "-h", db_host,
        "-u", db_user,
        f"-p{db_password}"
    ]
    run(mysql_cmd, check=False)


@cli.command()
def test():
    """Run smoke test on mock_api and MySQL."""
    ensure_env()

    # --- Mock API smoke test ---
    api_port = os.getenv("MOCK_API_PORT", "6000")
    payload = {"msg": "smoke-test"}
    try:
        r = requests.post(
            f"http://localhost:{api_port}/echo", json=payload, timeout=3)
        if r.ok and r.json().get("you_sent", {}).get("msg") == "smoke-test":
            click.echo(click.style("✅ mock_api echo passed", fg="green"))
        else:
            click.echo(click.style("⚠ mock_api echo failed", fg="yellow"))
    except requests.RequestException:
        click.echo(click.style("❌ mock_api unreachable", fg="red"))

    # --- MySQL ping test ---
    click.echo("Attempting mysql ping via docker-compose exec")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST", "localhost")

    # Pass password safely via -p flag
    mysql_cmd = [
        DOCKER_COMPOSE, "exec", "-T", "mysql",
        "mysqladmin", "ping",
        "-h", db_host,
        "-u", db_user,
        f"-p{db_password}",
    ]
    run(mysql_cmd, check=False)


@cli.command()
def doctor():
    """Run host pre-flight checks."""
    issues = []
    # Docker
    if shutil.which("docker") is None:
        issues.append("Docker not found in PATH")
    else:
        try:
            out = subprocess.check_output(
                ["docker", "version", "--format", "{{.Server.Version}}"], text=True)
            click.echo(f"🐳 Docker version {out.strip()}")
        except Exception:
            issues.append("Docker not responding")
    # Python
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    # Env
    if not os.path.exists(ENV_FILE):
        click.echo(click.style("ℹ .env not found (run init)", fg="yellow"))
    if issues:
        click.echo(click.style("❌ Issues detected:", fg="red"))
        for i in issues:
            click.echo("  - " + i)
    else:
        click.echo(click.style("✅ All checks passed", fg="green"))


@cli.command()
@click.argument("service", required=False)
def logs(service):
    """Tail docker logs."""
    cmd = [DOCKER_COMPOSE, "logs", "-f"]
    if service:
        cmd.append(service)
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        click.echo(click.style("\n🛑 log streaming stopped", fg="yellow"))


@cli.command()
def clean():
    """Stop containers and remove volumes."""
    run([DOCKER_COMPOSE, "down", "-v"])
    click.echo(click.style("🧹 Environment cleaned", fg="cyan"))


@cli.command()
@click.argument("name")
def add_mock(name):
    """Scaffold a new mock service."""
    mdir = os.path.join(ROOT, name)
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, "app.py"), "w") as f:
        f.write(
            "from flask import Flask,jsonify\napp=Flask(__name__)\n@app.route('/health')\ndef h():return jsonify({'status':'ok'})\napp.run(host='0.0.0.0',port=5000)")
    with open(os.path.join(mdir, "requirements.txt"), "w") as f:
        f.write("Flask\n")
    click.echo(click.style(f"✨ Mock service scaffolded at {mdir}", fg="green"))


if __name__ == "__main__":
    cli()
