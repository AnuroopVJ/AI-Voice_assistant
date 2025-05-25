import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
import os
# Initialize recognizer class (for recognizing the speech)
load_dotenv()
r = sr.Recognizer()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))
text = "" 


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
    chat_completion = client.chat.completions.create(
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": "You are a guy named Athul."
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": text,
            }
        ],

        # The language model which will generate the completion.
        model="llama-3.3-70b-versatile"
    )

    # Print the completion returned by the LLM.
    print(chat_completion.choices[0].message.content)

while True:
    text = speech_rec()
    if text == "[ERROR]":
        print("[ERROR]")
        continue
    elif text == "exit":
        break
    else:
        groq_chat(text)
        
    print("-------------------------------------------------")    