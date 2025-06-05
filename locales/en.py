# locales/en.py

TEXTS = {
    # Main menu
    "welcome": "👋 Hello! I am a bot that helps you view the class schedule.",
    "button_calendar": "📅 Calendar",
    "button_help": "❓ Help",
    "button_language": "🌐 Language",
    "main_menu": "Main menu:",
    "button_admin_menu": "👑 Administration",

    # Help
    "help_student": "Hello! I am a bot for viewing the schedule.\n\nAvailable commands:\n• /help - show this message\n• /calendar - open calendar management menu\n\nYou can use the \"Events for the week\" button in the calendar menu to view the schedule.",
    "help_admin": "Hello, administrator!\n\nAvailable commands:\n• /help - show this message\n• /calendar - open calendar management menu\n• /stats - view bot statistics\n• /broadcast - send message to all users\n\n",

    # Calendar
    "calendar_menu": "Calendar menu:",
    "button_create_event": "Create event",
    "button_week_events": "Events for the week",
    "button_delete_event": "Delete event",
    "button_back": "⬅️ Back",
    "create_event_name_prompt": "Enter event name:",
    "create_event_date_prompt": "Enter event date in DD.MM.YYYY format:",
    "create_event_date_empty": "Please enter the event date.",
    "create_event_date_invalid": "Invalid date format. Please use DD.MM.YYYY format.",
    "create_event_time_prompt": "Enter event start time in HH:MM format:",
    "create_event_time_empty": "Please enter the event start time.",
    "create_event_time_invalid": "Invalid time format. Please use HH:MM format.",
    "create_event_duration_prompt": "Enter event duration in hours (e.g., 1.5 for 1 hour 30 minutes):",
    "create_event_duration_invalid": "Invalid duration format. Please enter a number.",
    "create_event_description_prompt": "Enter event description (or '-' if no description):",
    "create_event_success": "Event successfully created!\n\nName: {summary}\nStart: {start_time}\nEnd: {end_time}\nDescription: {description}",
    "create_event_failed": "Failed to create event. Please try again.",
    "week_events_empty": "No events for the next 7 days.",
    "week_events_header": "Events for the next 7 days:\n\n",
    "week_events_item": "*{summary}*\nTime: {formatted_time}\nDescription: {description}\nID: `{event_id}`\n\n",
    "no_description": "No description",
    "delete_event_prompt": "Enter the event ID you want to delete:",
    "delete_event_empty_id": "Please enter the event ID to delete.",
    "delete_event_success": "Event with ID `{event_id}` successfully deleted.",
    "delete_event_failed": "Failed to delete event with ID `{event_id}`. Make sure the ID is correct and the event exists.",

    # Language
    "choose_language": "Choose interface language:",
    "language_changed": "Language successfully changed to {language_name}.",
    "unknown_language": "Unknown language. Please choose one of the suggested options.",

    # Admin functions (Administration Menu)
    "admin_menu": "Administration menu:",
    "button_stats": "📈 Statistics",
    "button_broadcast": "📢 Broadcast",
    "button_ban": "🚫 Ban",
    "button_back_to_main": "⬅️ Back to main menu",
    "stats_empty": "Statistics are empty.",
    "stats_header": "Command usage statistics:\n\n",
    "stats_item": "`{handler_name}`: `{count}`\n",
    "broadcast_prompt": "Enter the message to broadcast to all users:\n\n",
    "broadcast_empty": "Broadcast message cannot be empty.",
    "broadcast_sending": "Sending message:\n\n{broadcast_text}\n\nTotal users to broadcast: {user_count}...",
    "broadcast_complete": "Broadcast complete!\nSent: {sent_count}\nFailed to send: {failed_count}",
    "broadcast_cancelled": "Broadcast cancelled.",

    # General errors/messages
    "error_user_id_not_found": "Could not determine your User ID. Please try again later or contact an administrator.",
    "feature_for_students_only": "This feature is only available for students.",
} 