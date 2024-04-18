from h2o_wave import Q
import asyncio
import requests

async def stream_chatbot_response(user_input: str, q: Q):
    """
    Asynchronously streams chatbot responses to the client.

    This function takes user input, retrieves chatbot responses using an external service,
    and streams the responses back to the client one word at a time with a slight delay.

    Parameters:
        user_input (str): The input provided by the user to the chatbot.
        q (Q): The Q object representing the Wave client.

    """
    stream = ''
    for w in retrieve_chatbot_response(user_input).split():
        await asyncio.sleep(0.1)
        stream += w + ' '
        q.page['chat_bot'].data[-1] = [stream, False]
        await q.page.save()
    await q.page.save()


def retrieve_chatbot_response(user_input: str):
    # send to LLM backend, for now itll be placehold text
    bot_response = requests.post('http://localhost:4000/rag/query', json={'queries': [user_input]}).json()['replies'][user_input]
    return bot_response