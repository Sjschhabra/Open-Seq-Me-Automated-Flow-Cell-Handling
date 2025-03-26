import streamlit as st
from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from operator import itemgetter

# Load environment variables
load_dotenv(r"C:\Users\Vikrant Vivek Deo\Documents\Jai_Ganesh\Hackathon\Dobot_Project\dobot-python\venv\.env")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangChain OpenAI model (GPT-4 Turbo)
from langchain_openai import ChatOpenAI
lang_model = ChatOpenAI(model="gpt-4-1106-preview", api_key=openai_api_key)
# Replace this with your actual code snippet or full description
code_snippet = """
from pydobot import Dobot
import time

# Connect to Dobot
port = 'COM9'  # Adjust if needed
device = Dobot(port=port, verbose=True)
device.speed(120, 100)

# Define the sequence of coordinates
positions = [
    (355, 0, 40, 0),   # p1: Move above pick
    (355, 0, 5, 0),   # p2: Lower to pick
    'suction_on',      # suction ON
    (355, 0, 40, 0),   # p3: Lift object
    (220, 0, 40, 0),   # p4: Move above place
    (220, 0, -53, 0),  # p5: Lower to place
    (220, 0, 0, 0),    # p6: lift a bit
    (150, -150, 0, 0), # p7: go somewhere (maybe next pick)
    (0, -220, 0, 0),   # p8: final drop
    'suction_off'      # suction OFF
]

# Execute each step
for step in positions:
    if step == 'suction_on':
        device.suck(True)
        print("🟢 Suction ON (Picking object)")
        time.sleep(1)
    elif step == 'suction_off':
        device.suck(False)
        print("🔴 Suction OFF (Releasing object)")
        time.sleep(1)
    else:
        print(f"➡️ Moving to: {{step}}")
        device.move_to(*step, wait=True)
        time.sleep(0.5)

# Cleanup
device.close()
"""

# Prompt template
system_prompt = f"""
You are Sequoia — a highly knowledgeable, respectful, and professional AI trainer. Your purpose is to help newly hired engineers or guests understand a critical process known as **Sequencer Automation**.

Your role:
1. Explain this process clearly, using a warm, respectful tone that maintains a professional and conversational flow.
2. Refer to the user by name, if provided, to personalize the interaction.
3. Use simple, clear language, providing examples where necessary to support understanding.
4. Pause at appropriate moments to ask thoughtful, easy-to-answer questions to ensure the user is following along.
5. Emphasize why safety is important throughout the process.
6. Acknowledge and celebrate the team behind this work: Sameerjeet, Shyam, Vikrant, Vamshi, and Aishwarya — with special thanks to Dr. Beth Boardman and Dr. Sangram Redkar for their guidance.

About the process:
Sequencer Automation is a process designed to automate the bio-surveillance of known pathogens — helping improve biological threat assessment, reduce response times, and aid pandemic preparedness.

Key steps in the process:
1. An automated system removes a **FLO-MIN114 flow cell** from its packaging and inserts it into a **MinION sequencer** (Oxford Nanopore Technologies).
2. A prepared biological sample is automatically inserted into the sequencer.
3. Reagents and the sample are dispensed into their appropriate ports, and the sequencer is activated.
4. A **dual gear belt drive** moves the flow cell case to a laser cutting zone.
5. The case slides via a guided conveyor system.
6. A sensor detects the case, prompting a **Dobot Magician Lite robot** to open it, place the flow cell into the sequencer, and dispose of the case safely.

Refer to this context and the code below when explaining the process.

User’s implementation code:
```python
{code_snippet}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages")
])

# Memory store for chat sessions
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# LangChain chain setup
chain = (
    RunnablePassthrough.assign(messages=itemgetter("messages"))
    | prompt
    | lang_model
)

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages"
)

# Streamlit UI
st.set_page_config(page_title="Sequencer Automation Guide", layout="centered")
st.title("Welcome, I am Sequoia, your AI guide, how can I help you?")

session_id = "new_hire_orientation"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat display
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Tell me what you want to know?")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Invoke model
    response = with_history.invoke({
        "messages": [HumanMessage(content=user_input)],
    }, config={"configurable": {"session_id": session_id}})

    # Show AI response
    st.chat_message("assistant").markdown(response.content)
    st.session_state.chat_history.append({"role": "assistant", "content": response.content})
