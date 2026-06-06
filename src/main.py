import os, asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database import init_db, SessionLocal
from src.models import User
from src.tools import dispatch_tool
from src.bot import start, unsubscribe, newsletter, generate_newsletter, get_college, get_program, cancel

class MCPRequest(BaseModel):
    tool_name: str
    tool_args: dict = {}

bot_app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN", "mock_token")).build()
scheduler = AsyncIOScheduler()

async def scheduled_newsletter():
    session = SessionLocal()
    users = session.query(User).filter_by(is_active=True).all()
    for user in users:
        msg = await generate_newsletter(user.chat_id, user.program)
        try:
            await bot_app.bot.send_message(chat_id=user.chat_id, text=msg, parse_mode="MarkdownV2")
        except Exception as e:
            print(f"Failed to send to {user.chat_id}: {e}")
    session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Scheduler (Requirement 4 & 9)
    init_db()
    scheduler.add_job(scheduled_newsletter, 'interval', weeks=1)
    scheduler.start()
    
    # Init Bot Handlers (Requirements 5, 6, 8)
    
    # REQUIRED FIX: This is the ConversationHandler that asks the user for details!
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_college)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_program)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    bot_app.add_handler(conv_handler)
    
    # Other Handlers
    bot_app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    bot_app.add_handler(CommandHandler("newsletter", newsletter))
    
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    
    yield
    
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

# Requirement 7: MCP test endpoint
@app.post("/test-mcp-tool")
async def test_mcp_tool(req: MCPRequest):
    return dispatch_tool(req.tool_name, req.tool_args)