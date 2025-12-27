# =========================================================
# 🤖 TELEGRAM DEMO BOT — PRO • SAFE • DRY-RUN
# =========================================================
# Purpose:
# - Showcase a professional Telegram UX with a full
#   state machine, observability, validation, and controls.
# - NO external platform automation is executed.
# - All "sending" is simulated (dry-run).
#
# Why this exists:
# - You can design, test, and iterate UX/logic safely.
# - No policy violations, no account risk.
# =========================================================

import asyncio
import os
import re
import tempfile
import time
from typing import List, Dict, Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# 🔧 CONFIGURATION
# =========================
TG_BOT_TOKEN = "PASTE_TG_BOT_TOKEN"
OWNER_TG_ID = 7510461579

# =========================
# 🧠 GLOBAL STATE
# =========================
STATE: Dict[str, object] = {
    # auth / login (simulated)
    "logged_in": False,
    "session_label": None,      # user-provided label (simulated session)

    # flow
    "step": None,               # current input step
    "mode": None,               # "GC" (only GC shown in demo)
    "targets": [],              # selected target names (demo)
    "messages": [],             # payload messages
    "send_count": 0,            # 0 = infinite
    "running": False,           # engine on/off

    # telemetry
    "sent": 0,                  # simulated sent counter
    "started_at": None,         # run start time
    "task": None,               # asyncio task handle

    # demo data
    "mock_groups": [],          # cached demo groups
}

# =========================
# 🧰 UTILITIES
# =========================
def is_owner(uid: int) -> bool:
    return uid == OWNER_TG_ID

def now_ts() -> int:
    return int(time.time())

def uptime() -> int:
    if not STATE["started_at"]:
        return 0
    return now_ts() - STATE["started_at"]

def split_messages(raw: str) -> List[str]:
    """
    Split messages by & or 'and' with robust normalization.
    """
    raw = (
        raw.replace("﹠", "&")
           .replace("＆", "&")
           .replace("⅋", "&")
    )
    parts = re.split(r"\s*(?:&|\band\b)\s*", raw, flags=re.I)
    return [p.strip() for p in parts if p.strip()]

async def read_messages(update: Update) -> List[str]:
    """
    Read messages from text or uploaded .txt file.
    """
    if update.message.document:
        f = await update.message.document.get_file()
        tmp = tempfile.mktemp(".txt")
        await f.download_to_drive(tmp)
        with open(tmp, "r", encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
        os.remove(tmp)
        return split_messages(raw)
    return split_messages(update.message.text or "")

# =========================
# 🧪 DEMO DATA (SAFE)
# =========================
def build_mock_groups() -> List[str]:
    """
    Demo GC names to illustrate selection UX.
    """
    return [
        "AAKASH KUTIYA〘BETICHOD〙⚚ 💢",
        "Cudai Lounge 🔥",
        "Market Signals 📈",
        "Crypto Talk 💎",
        "Gaming Squad 🎮",
        "Misfits Boxing 🥊",
        "Design Critique ✍️",
        "Music Drops 🎵",
        "Startup Founders 🚀",
        "Late-Night Chat 🌙",
    ]

# =========================
# ⚙️ DRY-RUN ENGINE
# =========================
async def dry_run_engine():
    """
    Simulates ultra-fast sending without external calls.
    Respects COUNT (0 = infinite).
    """
    STATE["started_at"] = now_ts()
    STATE["sent"] = 0

    msgs = STATE["messages"]
    total = int(STATE["send_count"] or 0)

    if not msgs:
        STATE["running"] = False
        return

    i = 0
    while STATE["running"]:
        # simulate a send
        STATE["sent"] += 1
        i = (i + 1) % len(msgs)

        # COUNT-based stop
        if total > 0 and STATE["sent"] >= total:
            STATE["running"] = False
            break

        # yield to event loop (no speed throttling)
        await asyncio.sleep(0)

# =========================
# 🧭 COMMANDS
# =========================
async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    STATE.update({
        "logged_in": False,
        "session_label": None,
        "step": "session",
    })
    await update.message.reply_text(
        "🤖 *DEMO BOT ONLINE*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔐 *Login (Simulated)*\n"
        "Send any text as a *session label*.\n\n"
        "ℹ️ This is a dry-run demo.\n"
        "No external messages are sent.",
        parse_mode="Markdown"
    )

async def attack_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    if not STATE["logged_in"]:
        await update.message.reply_text("❌ Login first with `/start`")
        return
    STATE["step"] = "mode"
    await update.message.reply_text(
        "🚀 *SEND ENGINE SETUP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📍 *Destination*\n"
        "Reply with: `GC`",
        parse_mode="Markdown"
    )

async def stop_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    STATE["running"] = False
    if STATE["task"]:
        STATE["task"].cancel()
        STATE["task"] = None
    await update.message.reply_text(
        "🛑 *ENGINE HALTED*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⛔ Simulation stopped.\n"
        "✅ You can restart with `/attack`.",
        parse_mode="Markdown"
    )

async def status_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    await update.message.reply_text(
        "📊 *ENGINE DASHBOARD*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔐 *Logged In*     : {STATE['logged_in']}\n"
        f"📍 *Mode*          : {STATE['mode']}\n"
        f"🎯 *Targets*       : {len(STATE['targets'])}\n"
        f"📦 *Messages*      : {len(STATE['messages'])}\n"
        f"🔢 *Count*         : {STATE['send_count']} (0 = infinite)\n"
        f"📨 *Sent (demo)*   : {STATE['sent']}\n"
        f"⏱️ *Uptime*        : {uptime()}s\n"
        f"⚙️ *State*         : {'RUNNING' if STATE['running'] else 'IDLE'}",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    await update.message.reply_text(
        "🧭 *COMMAND CENTER*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "▶️ `/start`  — Begin demo login\n"
        "🚀 `/attack` — Configure send flow\n"
        "🛑 `/stop`   — Stop engine\n"
        "📊 `/status` — View status\n"
        "❓ `/help`   — This help\n\n"
        "ℹ️ Dry-run only • Safe demo",
        parse_mode="Markdown"
    )

# =========================
# 🔁 TEXT ROUTER (STATE MACHINE)
# =========================
async def text_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return
    text = (update.message.text or "").strip()
    step = STATE["step"]

    # ---- LOGIN (SIMULATED) ----
    if step == "session":
        STATE["logged_in"] = True
        STATE["session_label"] = text or "demo-session"
        STATE["step"] = None
        await update.message.reply_text(
            f"✅ *Logged In (Demo)*\n"
            f"Session: `{STATE['session_label']}`",
            parse_mode="Markdown"
        )
        return

    # ---- MODE ----
    if step == "mode" and text.lower() == "gc":
        STATE["mode"] = "GC"
        STATE["mock_groups"] = build_mock_groups()
        lines = [
            "📂 *AVAILABLE GROUP CHATS (DEMO)*",
            "━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]
        for i, name in enumerate(STATE["mock_groups"], 1):
            lines.append(f"🔹 `{i}` • {name}")
        lines.append("\n✍️ Send group number (e.g. `1`)")
        STATE["step"] = "gc_pick"
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    # ---- GC PICK ----
    if step == "gc_pick" and text.isdigit():
        idx = int(text) - 1
        if idx < 0 or idx >= len(STATE["mock_groups"]):
            await update.message.reply_text("❌ Invalid selection")
            return
        STATE["targets"] = [STATE["mock_groups"][idx]]
        STATE["step"] = "payload"
        await update.message.reply_text(
            "📝 *MESSAGE INPUT*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "• Type messages using `&`\n"
            "• Or upload a `.txt` file",
            parse_mode="Markdown"
        )
        return

    # ---- PAYLOAD ----
    if step == "payload":
        msgs = await read_messages(update)
        if not msgs:
            await update.message.reply_text("❌ No messages found")
            return
        STATE["messages"] = msgs
        STATE["step"] = "count"
        await update.message.reply_text(
            "🔢 *SEND COUNT*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `0` → Infinite\n"
            "• `10` → Send 10\n\n"
            "✍️ Send a number:",
            parse_mode="Markdown"
        )
        return

    # ---- COUNT ----
    if step == "count" and text.isdigit():
        STATE["send_count"] = int(text)
        STATE["running"] = True
        STATE["step"] = None
        if STATE["task"]:
            STATE["task"].cancel()
        STATE["task"] = asyncio.create_task(dry_run_engine())
        await update.message.reply_text(
            "🔥 *ENGINE LIVE (DEMO)*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚡ Speed: ULTRA (simulated)\n"
            f"🧮 Count: {STATE['send_count']} "
            f"({'Infinite' if STATE['send_count']==0 else 'Limited'})\n\n"
            "🟢 Running…",
            parse_mode="Markdown"
        )
        return

# =========================
# 🚀 MAIN
# =========================
def main():
    app = Application.builder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("attack", attack_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.ALL, text_router))
    app.run_polling()

if __name__ == "__main__":
    main()
