import asyncio

from google.adk import Runner
from google.adk.sessions import DatabaseSessionService

from constants import DB_URL, APP_NAME, USER_ID, REMINDERS
from memory_agent.agent import get_memory_agent
from utils import call_agent_async

# Using SQLITE Database for persistent storage
SESSION_SERVICE = DatabaseSessionService(db_url=DB_URL)

INITIAL_STATE = {
    "user_name": "Rahul Dey",
    REMINDERS: [],
}

async def get_session_id() -> str:
    """Fetch existing session for user id, if exists return the first one else create new one

    Return:
        session_id(str): Session id
    """
    # Checking for existing sessions for this user
    existing_sessions = await SESSION_SERVICE.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID
    )

    if existing_sessions and len(existing_sessions.sessions) > 0:
        session_id = existing_sessions.sessions[0].id
        print(f"Continuing with existing session: {session_id}")
        return session_id

    new_session = await SESSION_SERVICE.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=INITIAL_STATE,
    )
    print(f"Created new session: {new_session.id}")
    return new_session.id


async def main() -> None:
    session_id = await get_session_id()
    memory_agent = get_memory_agent()

    # Create a runner with the memory agent
    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=SESSION_SERVICE,
    )

    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to Memory Agent Chat!")
    print("Your reminders will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your data has been saved to the database.")
            break

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, session_id, user_input)


if __name__ == "__main__":
    asyncio.run(main())