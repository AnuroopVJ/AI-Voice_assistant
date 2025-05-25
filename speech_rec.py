import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
import os
from typing import List, Union

# Initialize recognizer class (for recognizing the speech)
load_dotenv()
r = sr.Recognizer()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))
text = "" 

from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam

# Initialize conversation history


conversation_history: List[
    Union[
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam
    ]
] = [
    ChatCompletionSystemMessageParam(
        role="system",
        content="You are a guy named Athul."
    )
]


def speech_rec() -> str:
    with sr.Microphone() as source:
        print("Talk")
        audio_text = r.listen(source)
        print("Time over, thanks")

        try:
            text = r.recognize_google(audio_text)
            # using google speech recognition
            print("Text: "+ text)
        except:
            text = "[ERROR]"
    return text
def groq_chat(text):
    # Add the user's message to the conversation history
    conversation_history.append(
        ChatCompletionUserMessageParam(
            role="user",
            content=text,
        )
    )

    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama-3.3-70b-versatile"
    )

    # Get the assistant's response
    assistant_response = chat_completion.choices[0].message.content

    # Add the assistant's response to the conversation history
    conversation_history.append(
        ChatCompletionAssistantMessageParam(
            role="assistant",
            content=assistant_response,
        )
    )

    # Print the assistant's response
    print(assistant_response)
    # Print the assistant's response
    print(assistant_response)

while True:
    text = speech_rec()
    if text == "[ERROR]":
        print("[ERROR]")
        continue
    elif text == "exit":
        break
    else:
        groq_chat(text)
        
    print("#-------------------------------------------------#")