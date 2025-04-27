import ollama
import aiConfig
import aiDebug

def print_debug_message(messages):
    aiDebug.debug_print(f" New request to model: ")
    for message in messages:
        aiDebug.debug_print(f"   {message['role']} : {message['content'][:100]}")

def get_model_answer_stream(messages):
    print_debug_message(messages)
    error = False
    try:
        stream = ollama.chat(
            model=aiConfig.AI_MODEL,
            messages=messages,
            stream=True
        )
    except Exception as e:
        aiDebug.debug_print(f"   Error during ollama.chat stream: {e}")
        error = True

    return stream, error

def get_model_answer(messages):
    print_debug_message(messages)
    error = False
    try:
        response = ollama.chat(
            model=aiConfig.AI_MODEL,
            messages=messages,
            stream=False
        )
        aiDebug.debug_print(f"   ANSWER: {response['message']['content'][:100]}")
        aiDebug
    except Exception as e:
        aiDebug.debug_print(f"   Error during ollama.chat: {e}")
        error = True

    return response['message']['content'], error