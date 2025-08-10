import asyncio
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from question_answering_agent.agent import question_answering_agent


APP_NAME = "Rahul's Assistance"
USER_ID = "rahul_dey"
SESSION_ID = str(uuid.uuid4())


async def main():
    # Create a new session to store state
    session_service_stateful = InMemorySessionService()

    initial_state = {
        "user_name": "Rahul Dey",
        "user_preferences": """
            I love to explore new technology with hands on experience from the comfort of my own space.
            My favorite food is Biryani.
            Currently I am watching the 'Special OPS 2' series, and I am loving it.
            I also love to travel and explore new thing from nature.
        """,
    }

    # Create a NEW session
    await session_service_stateful.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=initial_state
    )
    print(f"New session created with ID: {SESSION_ID}")

    runner = Runner(
        agent=question_answering_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="What is Rahul watching nowadays?")]
    )

    for event in runner.run(
        user_id=USER_ID, session_id=SESSION_ID, new_message=new_message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final Response: {event.content.parts[0].text}")

    print("============= Session Event Exploration ============")
    session = await session_service_stateful.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    # Log final Session State
    print("============= Final Session State ==============")
    for key, value in session.state.items() if session is not None else {}:
        print(f"{key}: {value}")


if __name__ == "__main__":
    print(
        "============== Starting the basic stateful session example ==================="
    )
    asyncio.run(main=main())
    print(
        "============== Completed the basic stateful session example ================="
    )
