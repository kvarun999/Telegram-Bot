from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.database import SessionLocal
from src.models import User
from src.tools import get_campus_events, get_course_reminders, get_weather_forecast
from src.llm import generate_section

# Conversation states
COLLEGE, PROGRAM = range(2)

def escape_md(text: str) -> str:
    escaped_chars = r"_*[]()~`>#+-=|{}.!"
    for char in escaped_chars:
        text = text.replace(char, f"\\{char}")
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! What college are you in?")
    return COLLEGE

async def get_college(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['college'] = update.message.text
    await update.message.reply_text("Great! And your program?")
    return PROGRAM

async def get_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    user = session.query(User).filter_by(chat_id=update.effective_chat.id).first()
    if not user:
        user = User(chat_id=update.effective_chat.id, college=context.user_data['college'], program=update.message.text, is_active=True)
        session.add(user)
    else:
        user.college = context.user_data['college']
        user.program = update.message.text
        user.is_active = True
    session.commit()
    session.close()
    await update.message.reply_text("Saved! Use /newsletter to get your update.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    user = session.query(User).filter_by(chat_id=update.effective_chat.id).first()
    if user:
        user.is_active = False
        session.commit()
    session.close()
    await update.message.reply_text("You have been unsubscribed.")

async def generate_newsletter(chat_id: int, program: str) -> str:
    events = get_campus_events()
    courses = get_course_reminders(program)
    weather = get_weather_forecast()
    
    events_text = await generate_section("events.j2", {"events": events})
    courses_text = await generate_section("courses.j2", {"courses": courses})
    weather_text = await generate_section("weather.j2", {"weather": weather})
    
    # Requirement 8 formatting
    msg = (
        f"*Events This Week*\n{escape_md(events_text)}\n\n"
        f"*Course Reminders*\n{escape_md(courses_text)}\n\n"
        f"*Weather Outlook*\n{escape_md(weather_text)}"
    )
    return msg

async def newsletter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Generating your newsletter... please wait.")
    session = SessionLocal()
    user = session.query(User).filter_by(chat_id=update.effective_chat.id).first()
    program = user.program if user else "General"
    session.close()
    
    msg = await generate_newsletter(update.effective_chat.id, program)
    await update.message.reply_text(msg, parse_mode="MarkdownV2")