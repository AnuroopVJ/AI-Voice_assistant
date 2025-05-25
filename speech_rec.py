import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
import os
import re
from duckduckgo_search import DDGS

# Initialize recognizer class (for recognizing the speech)
load_dotenv()
r = sr.Recognizer()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))
text = "" 
F = True


def speech_rec() -> str:
    with sr.Microphone() as source:
        print("Listeing...")
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


def search_tool(query: str):
    search =  DDGS()
    results = search.text(query, max_results=5)
    return results

# Set the system prompt
system_prompt = {
    "role": "system",
    "content":
    """
You are a smart and goal-driven ReAct agent. Follow the Thought → Action → Observation loop to solve tasks efficiently.\n

Think carefully before each step.

Use tools only when needed.
TOOLS AVAILABLE: search_tool 
Be concise but complete.

Stop when the final answer is reached.
DO NOT SAY UNNEEDED STUFF LIKE:
'Observation:Awaiting input...' or 'WAITING FOR OBSERVATION...'
Format:
Thought: [your reasoning here]
Action: [tool_name: input]
FAR@!: [if final anser is returned or not->NO or YES]
EXCECUTE

you'll be then given the result like this:
Observation: [result from tool]

if so:
Final Answer: [your answer]

FOLLOW THESE VERY STRICTLY"""
}

# chat history initialisation
chat_history = [system_prompt]

while True:
    if F:  # Only listen to the user if F is True
        # Get user input (speech to text conversion)
        speech_to_text = speech_rec()
        if speech_to_text == "[ERROR] An error occured":
            print("[ERROR] - An error occured. Please try again.")
            continue
        elif speech_to_text == "exit" or speech_to_text == "quit" or speech_to_text == "bye":
            break
        else:
            print(f"------------||User||------------ \n {speech_to_text}")
            print("------------||AI||------------")
            resp_from_groq = groq_chat_handling(speech_to_text)
            print(resp_from_groq)
    else:
        print("Continuing AI-driven execution...")

    if "Action:" in str(resp_from_groq):
        print("-----------TASK EXCECUTION-------------")

        # Extract the tool name and input from the response
        tool_name = re.search(r"Action:\s*(\w+_tool)", resp_from_groq)
        if tool_name is not None:  # Check if the tool name is found
            extracted_tool_name = tool_name.group(1)  # Extract the captured group (tool name)
            print(f"TOOL_NAME: {extracted_tool_name}")

            if extracted_tool_name == "search_tool":  # Check if the tool name is "search_tool"
                # Extract words after "search_tool:"
                tool_input = re.search(r"search_tool:\s*(.+)", resp_from_groq)
                if tool_input:
                    print(f"TOOL_ARG: {tool_input.group(1)}")  # Print the matched input
                    tool_input = tool_input.group(1)
                    result_s = search_tool(tool_input)
                    result_s = str(result_s)
                    print(result_s)
                    resp_from_groq = groq_chat_handling(result_s)
                    print(resp_from_groq)
                else:
                    print("[ERROR] Could not extract tool input.")
            else:
                print("[ERROR] Tool name is not recognized.")
        else:
            print("[ERROR] Could not extract tool name.")

    if "FAR@!:" in str(resp_from_groq):
        y_n = re.search(r"FAR@!:\s*(YES|NO)", resp_from_groq)
        if y_n:
            if y_n.group(1) == "YES":
                F = True
            elif y_n.group(1) == "NO":
                F = False
