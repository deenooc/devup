#!/usr/bin/env python3
import os
import subprocess
import sys
from shutil import copyfile

import click
import requests
from dotenv import dotenv_values, set_key, load_dotenv

ROOT = os.path.dirname(__file__)
ENV_EXAMPLE = os.path.join(ROOT, ".env.example")
ENV_FILE = os.path.join(ROOT, ".env")
DOCKER_COMPOSE_CMD = os.environ.get("DOCKER_COMPOSE", "docker-compose")


def run(cmd, check=True):
    print(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    print(proc.stdout)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(cmd)} failed with {proc.returncode}")
    return proc


@click.group()
def cli():
    """DevUp — automate local onboarding environment."""
    pass


@cli.command()
def init():
    """Create .env from .env.example and fill defaults if missing."""
    if not os.path.exists(ENV_EXAMPLE):
        click.echo(".env.example not found")
        sys.exit(1)
    if os.path.exists(ENV_FILE):
        click.confirm(".env already exists. Overwrite?", abort=True)
    copyfile(ENV_EXAMPLE, ENV_FILE)
    click.echo("Created .env from .env.example")
    # load and show summary
    vals = dotenv_values(ENV_FILE)
    click.echo("Environment variables:")
    for k, v in vals.items():
        click.echo(f"  {k}={v}")


@cli.command()
@click.option("--detach/--no-detach", default=True, help="Run docker-compose detached")
def up(detach):
    """Start the local environment with docker-compose."""
    cmd = [DOCKER_COMPOSE_CMD, "up"]
    if detach:
        cmd.append("-d")
    run(cmd)


@cli.command()
def status():
    """Check the status of mock_api and MySQL."""
    load_dotenv(ENV_FILE)

    # --- Mock API status ---
    api_port = os.environ.get("MOCK_API_PORT", "6000")
    api_url = f"http://localhost:{api_port}/health"
    try:
        r = requests.get(api_url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == "ok":
            click.echo(f"[OK] mock_api at {api_url}")
        else:
            click.echo(
                f"[WARN] mock_api unexpected response: {r.status_code} {r.text}")
    except Exception as e:
        click.echo(f"[ERR] Cannot reach mock_api at {api_url}: {e}")

    # --- MySQL status ---
    click.echo("Attempting mysql ping via docker-compose exec")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST", "localhost")

    mysql_cmd = [
        DOCKER_COMPOSE_CMD, "exec", "-T", "mysql",
        "mysqladmin", "ping",
        "-h", db_host,
        "-u", db_user,
        f"-p{db_password}"
    ]
    run(mysql_cmd, check=False)


@cli.command()
def test():
    """Run a smoke test: mock_api echo and mysql ping."""
    load_dotenv(ENV_FILE)

    # --- Mock API smoke test ---
    api_port = os.environ.get("MOCK_API_PORT", "6000")
    api_url = f"http://localhost:{api_port}/echo"
    payload = {"msg": "smoke-test"}
    try:
        r = requests.post(api_url, json=payload, timeout=3)
        if r.status_code == 200 and r.json().get("you_sent", {}).get("msg") == "smoke-test":
            click.echo("[OK] mock_api echo test passed")
        else:
            click.echo(
                f"[WARN] mock_api echo test unexpected response: {r.status_code} {r.text}")
    except Exception as e:
        click.echo(f"[ERR] mock_api echo failed: {e}")

    # --- MySQL ping test ---
    click.echo("Attempting mysql ping via docker-compose exec")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST", "localhost")

    # Pass password safely via -p flag (no space!)
    mysql_cmd = [
        DOCKER_COMPOSE_CMD, "exec", "-T", "mysql",
        "mysqladmin", "ping",
        "-h", db_host,
        "-u", db_user,
        f"-p{db_password}",
    ]
    run(mysql_cmd, check=False)


@cli.command()
def clean():
    """Tear down the environment and remove volumes."""
    run([DOCKER_COMPOSE_CMD, "down", "-v"])


@cli.command()
@click.argument("name")
def add_mock(name):
    """Create a tiny mock service skeleton (not fully automated: convenience helper)."""
    click.echo(f"Creating mock service scaffolding for: {name}")
    mdir = os.path.join(ROOT, name)
    if os.path.exists(mdir):
        click.echo("Directory already exists, aborting.")
        return
    os.makedirs(mdir)
    with open(os.path.join(mdir, "app.py"), "w") as f:
        f.write(
            "# simple flask mock\nfrom flask import Flask, jsonify\napp = Flask(__name__)\n@app.route('/health')\ndef health():\n    return jsonify({'status':'ok'})\nif __name__=='__main__':\n    app.run(host='0.0.0.0', port=6000)\n")
    with open(os.path.join(mdir, "requirements.txt"), "w") as f:
        f.write("Flask\n")
    click.echo("Scaffold created. Add to docker-compose.yml manually.")


if __name__ == "__main__":
    cli()
