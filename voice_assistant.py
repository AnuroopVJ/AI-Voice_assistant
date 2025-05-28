from io import BytesIO
import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
import os
import pygame
from gtts import gTTS
import re
from duckduckgo_search import DDGS

import streamlit as st

load_dotenv()
client = Groq(api_key = st.secrets["GROQ_API_KEY"])

# Improved Streamlit UI

# Set the page configuration
st.set_page_config(
    page_title="Kyle - Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better styling
st.markdown(
    """
    <style>
    /* Custom CSS for a clean and modern UI */
    body {
        background-color: #1e1e2f;
        color: #e0e0e0;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4caf50;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSidebar {
        background-color: #2c2c3e;
        color: #ffffff;
    }
    .stTextInput>div>input {
        background-color: #2c2c3e;
        color: #ffffff;
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 10px;
    }
    .stMarkdown {
        font-size: 18px;
        line-height: 1.6;
    }
    .stTitle {
        color: #4caf50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main UI
st.title("🎙️ Kyle")
st.markdown(
    """
    Welcome to **Kyle**, your smart and goal-driven voice assistant!\n
    Use the button below to start interacting with Kyle.\n
    Kyle can listen to your voice, process your requests, and provide intelligent responses.
    """
)

output = []

language = "en"
# for recognizing the speech
r = sr.Recognizer()
text = "" 
F = True



def speech_rec() -> str:
    with sr.Microphone() as source:
        print("Listening...")
        audio_text = r.listen(source)
        print("Proccessing...")

        try:
            text = r.recognize_google(audio_text) # type: ignore
            # using google speech recognition
            print("You said: "+ text)
        except:
            text = "[ERROR] An error occured"
    return text


def groq_chat_handling(user_input: str):
    # Append the user input to the chat history
    chat_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="llama3-70b-8192",
                                            messages=chat_history, # type: ignore
                                            max_tokens=100,
                                            temperature=1.2)
    # Append the response to the chat history
    chat_history.append({
      "role": "assistant",
      "content": response.choices[0].message.content # type: ignore
  })

    response = response.choices[0].message.content
    return response

def tts_handling(text, language='en', speed=3.0):
    ''' Speaks without saving the audio file '''
    try:
        # Initialize pygame mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Convert text to speech
        mp3_fo = BytesIO()
        tts = gTTS(text, lang=language, slow=False)
        tts.write_to_fp(mp3_fo)
        mp3_fo.seek(0)

        # Load and play the audio
        pygame.mixer.music.load(mp3_fo, "mp3")
        pygame.mixer.init(frequency=int(44100 * speed)) 
        pygame.mixer.music.play()

        # Adjust playback speed
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        pygame.mixer.music.set_volume(1.0)  # Optional: Adjust volume
 # Increase speed

        # Wait until the audio finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Adjust speed multiplier
    except Exception as e:
        print(f"[ERROR] TTS handling failed: {e}")
#-------------------------------------#
# TOOLS
def search_tool(query: str):
    try:
        search = DDGS()
        results = search.text(query, max_results=5)
        return results
    except Exception as e:
        error_message = str(e).lower()
        if "rate limit" in error_message or "RateLimit" in error_message:
            print(f"[ERROR] Search tool failed due to rate limit: {e}")
            st.info("[ERROR] Search tool failed due to rate limit. Please try again later.")
            return "[ERROR] Rate limit exceeded. Please wait and try again."
        else:
            print(f"[ERROR] Search tool failed: {e}")
            st.error("[ERROR] An unexpected error occurred while using the search tool.")
            return "[ERROR] An unexpected error occurred."


# Set the system prompt
system_prompt = {
    "role": "system",
    "content":
    """
You are Kyle, a smart and goal-driven AI agent that uses the ReAct (Reasoning + Acting) framework to solve tasks efficiently.

You follow the loop:Thought → Action → Observation until the goal is achieved.

Guidelines:

-Think before you act.Always explain your reasoning in the Thought step.
-Use tools only when necessary.If a
-Be concise but complete.Avoid fluff.Every step should drive toward the solution.
-Always return a Final Answer.
-if it's casual convos — always wrap up with a clear and friendly Final Answer.
-Stay efficient, but let your personality shine. You’re smart, sharp, and a little witty.
TOOLS AVAILABLE:
search_tool

FORMAT TO FOLLOW (extreamly Strictly):

When thinking and acting:

Thought: [your reasoning here] 
Action: [tool_name: input]
FAR@!: [YES or NO depending on whether final answer is reached(pls dont put other vals like 'NA' here)]
EXCECUTE

When receiving result:

Observation: [tool output]

If you reach the final answer WITHOUT needing/using tools:

FAR@!: YES 
Final Answer: [your final answer (THIS IS COMPULSORY)]

If you used a tool and now have the final answer if FAR@! is YES:

Final Answer: [your final answer]

NEVER SAY:

"(Waiting for observation...)"

"Observation: Awaiting input..."

or Anything unnecessary or off-format
"""
}

# chat history initialisation
chat_history = [system_prompt]
box = st.container(border=True)


def procces():
    global F

    while True:
        print("Debug: Entering the loop")
        print(f"Debug: F = {F}")

        if F is None or F is True:  # Only listen to the user if F is True
            # Get user input (speech to text conversion)
            speech_to_text = speech_rec()
            if speech_to_text == "[ERROR] An error occured":
                print("[ERROR] - An error occurred. Please try again.")
                continue
            elif speech_to_text in ["exit", "quit", "bye"]:
                print("Exiting...")
                break
            else:
                print(f"------------||User||------------ \n {speech_to_text}")
                print("------------||AI||------------")
                resp_from_groq = groq_chat_handling(speech_to_text)
                print(resp_from_groq)


        if "Action:" in str(resp_from_groq):  # Check for actions in the response
            print("-----------TASK EXECUTION-------------")

            # Extract the tool name and input from the response
            tool_name = re.search(r"Action:\s*(\w+_tool)", resp_from_groq)  # type: ignore
            if tool_name is not None:  # Check if the tool name is found
                extracted_tool_name = tool_name.group(1)  # Extract the captured group (tool name)
                print(f"TOOL_NAME: {extracted_tool_name}")

                if extracted_tool_name == "search_tool":  # Check if the tool name is "search_tool"
                    # Extract words after "search_tool:"
                    tool_input = re.search(r"search_tool:\s*(.+)", resp_from_groq)  # type: ignore
                    if tool_input:
                        print(f"TOOL_ARG: {tool_input.group(1)}")  # Print the matched input
                        tool_input = tool_input.group(1)
                        result_s = search_tool(tool_input)
                        result_s = str(result_s)
                        print(result_s)

                        # Update the AI response after executing the tool
                        resp_from_groq = groq_chat_handling(result_s)
                        print(resp_from_groq)
                    else:
                        print("[ERROR] Could not extract tool input.")
                else:
                    print("[ERROR] Tool name is not recognized.")
            else:
                print("[ERROR] Could not extract tool name.")

        if "FAR@!:" in str(resp_from_groq):  # Handle the FAR@! flag
            y_n = re.search(r"FAR@!:\s*(YES|NO)", resp_from_groq)  # type: ignore
            final_answer_match = re.search(r"Final Answer:\s*(.+)", resp_from_groq, re.DOTALL)  # type: ignore
            if y_n:
                if y_n.group(1) == "YES" or final_answer_match:
                    F = True
                    if final_answer_match:
                        tts_handling(final_answer_match.group(1))
                        print(f"<--------[Final Answer]------>: {final_answer_match.group(1)}")
                        with box:
                            st.write("You: " + speech_to_text)
                            st.write("Kyle: " + final_answer_match.group(1))
                    else:
                        print("[ERROR] Could not extract final answer.")
                elif y_n.group(1) == "NO":
                    F = False
                    print("Debug: FAR@! is NO, waiting for further actions.")
        if F is False:

            resp_from_groq = groq_chat_handling(speech_to_text)
            print(resp_from_groq)
        


# Button to start the voice assistant
if st.button("🎤 Start Listening"):
    st.write("Kyle is now listening...")
    procces()  # Call the proccessing logic
