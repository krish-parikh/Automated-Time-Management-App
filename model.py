# pip install openai kor langchain
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text, Number
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    max_tokens=200,
    openai_api_key = "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",
)

schema = schema = Object(
    id="event_info",
    description="Information about a given event.",
    attributes=[
        Text(
            id="event_name",
            description="Name of the event",
        ),
        Text(
            id="event_time",
            description="Time of event in 'HH:MM' format. If time is not explicitly mentioned, use context to determine time of day",
            examples=[
                ("I am going out this evening at 6 to 7", "18:00, 19:00"),
                ("I am going out to eat tonight", "evening"),
            ],
        ),
        Text(
            id="event_date",
            description="Date in 'DD, MM' format except for days of the week and phrases like 'tomorrow'",
            examples=[
                ("I have a meeting on the 12th of June", "12, 06"),
            ],
        ),
        Number(
            id="event_importance",
            description="Determine the importance of the event and give a score from 1-5, with 5 being critical",
            examples=[
                ("I am going out with my friends tomorrow", '3'),
            ],
        ),
        Number(
            id="event_flexibility",
            description="Determine the flexibility of the event and give a score of 2 for movable and 1 for not movable",
            examples=[
                ("I have meeting scheduled at school tomorrow", '1'),
            ],
        ),
    ],
    examples=[
        (
            "I'm going shopping this evening at 6, to buy groceries for my sister's party on the 12th of June.",
            [
                {"event_name": "Grocery Shopping", "event_time": "18:00, ", "event_location": "Shops", "event_importance": 2, "event_flexibility": 2},
                {"event_name": "Sister's Birthday Party", "event_date": "12, 06", "event_importance": 5, "event_flexibility": 1},
            ],
        ),
    ],
    many=True,
)

def get_event_info(text, llm = llm, schema = schema):
    chain = create_extraction_chain(llm, schema)
    response = chain.run(text)["data"]
    return response