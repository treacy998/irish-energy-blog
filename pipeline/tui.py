#!/usr/bin/env python3
"""
blog — INIS Energy Blog CLI
Simple numbered menu, Rich display, VS Code for editing.
"""

import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

ROOT        = Path(__file__).parent.parent

# ── Logging ────────────────────────────────────────────────────────────────
LOG_FILE = ROOT / "blog.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("blog")
log.info("="*60)
log.info("blog TUI started")
SITE_DIR    = ROOT / "site"
CONTENT_DIR = SITE_DIR / "content"
DAILY_DIR   = CONTENT_DIR / "daily"
WEEKLY_DIR  = CONTENT_DIR / "weekly"
DATA_DIR    = ROOT / "data"
HUGO        = Path.home() / ".local" / "bin" / "hugo"

console = Console()


def ask(prompt: str, default: str = "") -> str:
    try:
        val = input(f"  {prompt}" + (f" [{default}]" if default else "") + ": ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print()
        return ""


def confirm(prompt: str) -> bool:
    val = ask(f"{prompt} (y/N)").lower()
    return val in ("y", "yes")


def pick(choices: list[tuple[str, str]]) -> str | None:
    """Display numbered choices, return the key of the selection."""
    for i, (key, label) in enumerate(choices, 1):
        console.print(f"  [bold cyan]{i}[/bold cyan]  {label}")
    console.print()
    raw = ask("Enter number")
    if not raw:
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return choices[idx][0]
    except ValueError:
        pass
    console.print("  [dim]Invalid choice.[/dim]")
    return None


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm


def toggle_draft(path: Path) -> bool:
    text = path.read_text()
    if "draft: true" in text:
        path.write_text(text.replace("draft: true", "draft: false", 1))
        return False
    else:
        path.write_text(text.replace("draft: false", "draft: true", 1))
        return True


def get_all_posts() -> list[dict]:
    posts = []
    for section_dir, section in [(DAILY_DIR, "daily"), (WEEKLY_DIR, "weekly")]:
        if not section_dir.exists():
            continue
        for md in sorted(section_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
            fm = parse_frontmatter(md)
            posts.append({
                "path":    md,
                "title":   fm.get("title", md.stem),
                "date":    fm.get("date", ""),
                "section": section,
                "draft":   fm.get("draft", "false").lower() == "true",
            })
    return posts


def open_vscode(path: Path):
    subprocess.Popen(["code", str(path)])
    console.print(f"  [dim]Opened in VS Code → {path.name}[/dim]")


def show_header():
    console.print()
    console.print(Panel(
        "[bold cyan]INIS Energy Blog[/bold cyan]  [dim]·  irish-energy-blog.vercel.app[/dim]",
        box=box.ROUNDED,
        padding=(0, 2),
        expand=False,
    ))
    console.print()


def main_menu():
    log.info("Entering main menu")
    while True:
        console.clear()
        show_header()

        key = pick([
            ("daily",   "New daily briefing    (run pipeline)"),
            ("post",    "New post               (blank, manual)"),
            ("manage",  "Manage posts"),
            ("preview", "Preview site           (localhost:1313)"),
            ("deploy",  "Deploy to Vercel"),
            ("quit",    "Quit"),
        ])

        log.info("Menu selection: %s", key)

        if   key == "daily":   new_daily()
        elif key == "post":    new_post()
        elif key == "manage":  manage_posts()
        elif key == "preview": preview_site()
        elif key == "deploy":  deploy()
        elif key == "quit":    sys.exit(0)
        elif key is None:      continue

        console.print()
        ask("Press Enter to return to menu…")


def new_daily():
    log.info("new_daily: started")
    console.print()
    console.rule("[cyan]New Daily Briefing[/cyan]")
    console.print()

    semo_files = sorted(
        DATA_DIR.glob("MarketResult_SEM-DA_*.csv"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    ) if DATA_DIR.exists() else []

    log.info("new_daily: found %d SEMO files in %s", len(semo_files), DATA_DIR)

    if not semo_files:
        console.print("[yellow]  No SEMO CSV found in data/[/yellow]")
        console.print("  Drop a [bold]MarketResult_SEM-DA_*.csv[/bold] into the data/ folder first.")
        log.warning("new_daily: aborted — no SEMO data files")
        return

    latest = semo_files[0]
    log.info("new_daily: using %s", latest.name)
    console.print(f"  Using: {latest.name}\n")

    pipeline_script = ROOT / "pipeline" / "run_daily.py"
    log.info("new_daily: running pipeline %s (cwd=%s)", pipeline_script, ROOT / "pipeline")
    result = subprocess.run(
        [sys.executable, str(pipeline_script)],
        cwd=ROOT / "pipeline",
    )
    log.info("new_daily: pipeline exit code %d", result.returncode)

    if result.returncode != 0:
        console.print("\n  [red]Pipeline failed. Check output above.[/red]")
        log.error("new_daily: pipeline failed")
        return

    if DAILY_DIR.exists():
        newest = sorted(DAILY_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        if newest:
            log.info("new_daily: opening %s in VS Code", newest[0].name)
            console.print(f"\n  [green]Scaffolded:[/green] {newest[0].name}")
            open_vscode(newest[0])


def new_post():
    log.info("new_post: started")
    console.print()
    console.rule("[cyan]New Post[/cyan]")
    console.print()

    section_key = pick([
        ("daily",  "Daily briefing"),
        ("weekly", "Weekly deep-dive"),
    ])
    if not section_key:
        return

    default_title = (
        f"DAM Market Update – {datetime.now().strftime('%d %b %Y')}"
        if section_key == "daily"
        else f"Weekly Analysis – {datetime.now().strftime('%d %b %Y')}"
    )

    title = ask("Post title", default=default_title)
    if not title:
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    slug     = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    filename = f"{date_str}-{slug}.md"

    target_dir = DAILY_DIR if section_key == "daily" else WEEKLY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    post_path = target_dir / filename

    if post_path.exists():
        console.print(f"  [yellow]File already exists:[/yellow] {filename}")
        if not confirm("Overwrite?"):
            return

    log.info("new_post: creating %s (section=%s)", post_path, section_key)
    post_path.write_text(
        f"""---
title: "{title}"
date: {date_str}
draft: true
tags: []
description: ""
---

<!-- Add your content here. Charts can be embedded with: -->
<!-- ![Alt text](/charts/your-chart.png) -->

"""
    )

    console.print(f"\n  [green]Created:[/green] {post_path.relative_to(ROOT)}")
    console.print("  [dim]Draft is true — publish via Manage Posts when ready.[/dim]")
    open_vscode(post_path)


def manage_posts():
    while True:
        console.print()
        console.rule("[cyan]Manage Posts[/cyan]")
        console.print()

        posts = get_all_posts()
        if not posts:
            console.print("  [dim]No posts found.[/dim]")
            return

        table = Table(box=box.SIMPLE_HEAD, show_edge=False, pad_edge=False)
        table.add_column("#",       width=4, style="dim")
        table.add_column("Title",   min_width=38, no_wrap=True)
        table.add_column("Date",    width=12, style="dim")
        table.add_column("Section", width=8,  style="dim")
        table.add_column("Status",  width=9)

        for i, p in enumerate(posts, 1):
            status = "[yellow]Draft[/yellow]" if p["draft"] else "[green]Live [/green]"
            table.add_row(str(i), p["title"][:50], p["date"], p["section"], status)

        console.print(table)
        console.print()

        raw = ask("Post number to manage (or Enter to go back)")
        if not raw:
            return
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(posts):
                if not _post_actions(posts[idx]):
                    return
            else:
                console.print("  [dim]Out of range.[/dim]")
        except ValueError:
            console.print("  [dim]Enter a number.[/dim]")


def _post_actions(post: dict) -> bool:
    console.print()
    console.print(f"  [bold]{post['title'][:60]}[/bold]")
    console.print()

    draft_label = "Publish now  (set draft: false)" if post["draft"] else "Unpublish    (set draft: true)"
    key = pick([
        ("edit",   "Edit in VS Code"),
        ("toggle", draft_label),
        ("delete", "Delete permanently"),
        ("back",   "Back to post list"),
    ])

    if key == "edit":
        open_vscode(post["path"])

    elif key == "toggle":
        is_draft = toggle_draft(post["path"])
        label = "[yellow]draft[/yellow]" if is_draft else "[green]live[/green]"
        console.print(f"\n  Post is now {label}.")

    elif key == "delete":
        if confirm(f"Delete '{post['title'][:50]}'? Cannot be undone."):
            post["path"].unlink()
            console.print("  [red]Deleted.[/red]")
            return False

    return True


def preview_site():
    log.info("preview_site: starting Hugo server (hugo=%s, cwd=%s)", HUGO, SITE_DIR)
    console.print()
    console.rule("[cyan]Preview Site[/cyan]")
    console.print()
    console.print("  Open [bold cyan]http://localhost:1313[/bold cyan] in your browser.")
    console.print("  [dim]Press Ctrl+C to stop the server.[/dim]\n")

    if not HUGO.exists():
        log.error("preview_site: Hugo not found at %s", HUGO)
        console.print(f"  [red]Hugo not found at {HUGO}[/red]")
        console.print("  Run: wget https://github.com/gohugoio/hugo/releases/... or check your install.")
        return

    try:
        result = subprocess.run(
            [str(HUGO), "server", "-D", "--logLevel", "error"],
            cwd=SITE_DIR,
        )
        log.info("preview_site: Hugo exited with code %d", result.returncode)
    except KeyboardInterrupt:
        log.info("preview_site: stopped by user (Ctrl+C)")
        console.print("\n  [dim]Server stopped.[/dim]")


def deploy():
    log.info("deploy: started")
    console.print()
    console.rule("[cyan]Deploy to Vercel[/cyan]")
    console.print()

    default_msg = f"content: publish {datetime.now().strftime('%Y-%m-%d')}"
    message = ask("Commit message", default=default_msg)
    if not message:
        return

    console.print()
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", message],
        ["git", "push"],
    ]

    for cmd in commands:
        console.print(f"  [dim]$ {' '.join(cmd)}[/dim]")
        log.info("deploy: running %s", " ".join(cmd))
        result = subprocess.run(cmd, cwd=ROOT)
        log.info("deploy: %s exit code %d", cmd[1], result.returncode)
        if result.returncode != 0 and cmd[1] != "commit":
            log.error("deploy: command failed: %s", " ".join(cmd))
            console.print("  [red]Failed.[/red]")
            return

    log.info("deploy: completed successfully")
    console.print(f"\n  [green]Pushed.[/green] Vercel will deploy in ~30 seconds.")
    console.print(f"  [dim]→  https://irish-energy-blog.vercel.app[/dim]")


if __name__ == "__main__":
    try:
        log.info("Python %s, sys.executable=%s", sys.version.split()[0], sys.executable)
        log.info("ROOT=%s, HUGO=%s", ROOT, HUGO)
        log.info("HUGO exists: %s", HUGO.exists())
        main_menu()
    except (KeyboardInterrupt, EOFError):
        log.info("Exited via Ctrl+C / EOF")
        console.print("\n\n  [dim]Bye.[/dim]")
        sys.exit(0)
    except Exception as e:
        log.exception("Unhandled exception: %s", e)
        raise
