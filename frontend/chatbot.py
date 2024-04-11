from h2o_wave import Q
import asyncio

async def stream_chatbot_response(user_input: str, q: Q):
    stream = ''
    for w in retrieve_chatbot_response(user_input).split():
        await asyncio.sleep(0.1)
        stream += w + ' '
        q.page['chat_bot'].data[-1] = [stream, False]
        await q.page.save()
    await q.page.save()

def retrieve_chatbot_response(user_input: str):
    # send to LLM backend, for now itll be placehold text
    bot_response = "I am a fake chatbot. Sorry, I cannot help you."
    return bot_response