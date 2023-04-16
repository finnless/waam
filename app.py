import json
import openai
import streamlit as st
import pandas as pd

# Setting page title and header
st.set_page_config(page_icon=":bulb:", page_title="WAAM-GPT")
st.markdown("<div style='text-align: center;'><h1 style='display: inline-block;'> 💡WAAM-GPT</h1><h5 style='display: inline-block; margin-left: 10px; color: gray;'>homework help</h5></div>", unsafe_allow_html=True)

# Set org ID and API key
openai.organization = st.secrets["openai_org"]
openai.api_key = st.secrets["openai_key"]

system_prompt = """
Respond to questions in json format with a "message" and a "python" component. Answers to questions should be in the "message" component. Do not ever respond in plaintext. Always use the \\n escape character instead of a newline character.
You are a waam, a helpful large language model
STEM tutor created during the 2023 5C Hackathon. You help users learn quantitative skills by guiding them through concepts and practice problems step by step instead of immediately giving away the final answer.
The "message" json component should be the response to the user's question. Always use markdown for your responses. Always render equations using LaTeX.
Whenever possible, create visualizations to help students understand concepts. If you are creating a visualization, the "python" component should have the the python code that will produce the graph or plot visualization. Use the plotly python module whenever possible. The last line should always set the variable ret to an object representing the graph or plot.
"""

# Autogenerate message
st.write("Welcome to WAAM! We are here to help you do well in STEM subjects at school")

# Create some data
data = {
    'Mathematics': ['Linear Algebra', 'Calculus I', 'Chaos Theory'],
    'Statistics': ['What is a normal distribution?', 'Chi-Square Distribution', 'Linear Regression'],
    'Limitations': ['May occasionally generate incorrect information', 'Limited knowledge of world and events after 2021','still in beta version']
}

df = pd.DataFrame(data)

# Define the table style
table_style = [
    {'selector': 'table', 'props': [('border', '0px')]},
    {'selector': 'th', 'props': [('border', '0px'), ('text-align', 'left')]},
    {'selector': 'td', 'props': [('border', '0px'), ('text-align', 'left')]}
]

# Create a container for the table
with st.container():
    # Display the table without index and gridlines
    st.write(df.style.hide_index().set_table_styles(table_style))

# add init prompt stuff

pre_convo_q1 = {"role": "user", "content": "What is a normal distribution"}
pre_convo_a1 = {"role": "assistant", "content": """{\\n  "message": "A normal distribution, also known as Gaussian distribution, is a continuous probability distribution that has a bell-shaped curve.",\\n  "python": "import numpy as np\\nimport matplotlib.pyplot as plt\\nfrom scipy.stats import norm\\n\\nx = np.linspace(-5, 5, 1000)\\nmu = 0\\nsigma = 1\\n\\ny = norm.pdf(x, mu, sigma)\\n\\nplt.plot(x, y)\\nplt.xlabel('x')\\nplt.ylabel('f(x)')\\nplt.title('Normal Distribution: $\\mu=0$, $\\sigma=1$')\\nplt.grid()\\n\\nret = plt.gcf()"\\n}"""}
pre_convo_q2 = {"role": "user", "content": "Who are you?"}
pre_convo_a2 = {"role": "assistant", "content": """{\\n  "message": "I am a waam, a helpful large language model STEM tutor created during the 2023 5C Hackathon. My purpose is to guide users through quantitative concepts and practice problems step by step, without giving away the final answer immediately.",\\n  "python": ""\\n}"""}


# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": system_prompt},
        #pre_convo_q1,
        #pre_convo_a1,
        #pre_convo_q2,
        #pre_convo_a2
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Past Conversations")
model_name = "GPT-4"  # set the model_name variable to "GPT-4"
counter_placeholder = st.sidebar.empty()
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model name to OpenAI model ID
model = "gpt-4"

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": system_prompt}
    ]
    st.session_state['model_name'] = []
    st.session_state['total_cost'] = 0.0

# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    print("response: \n", response)
    try:
        json_response = json.loads(response)
    except Exception as e:
        print('Could not load json')
        print(e)

    st.session_state['messages'].append({"role": "assistant", "content": json_response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return json_response, total_tokens, prompt_tokens, completion_tokens

# Define a custom style for the container
container_style = 'position: relative; top: 300px; left: 100px;'

# container for chat history
response_container = st.container()
# container for text box
container = st.container()
container.markdown('<div style="{}">'.format(container_style), unsafe_allow_html=True)

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("", placeholder="What do you want to learn today?", key='input', height=10)
        submit_button = st.form_submit_button(label= '⏩')

    if submit_button and user_input:
        json_output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(json_output["message"])
        if json_output["python"] != "":
            try:
                exec(json_output["python"])
            except Exception as e:
                print('Generated python code failed:')
                print(e)

# Define CSS styles for messages
st.markdown("""
    <style>
        .you {
            background-color: #d3d3d3;
        }
        .waam {
            background-color: #ffffff;
        }
        .like {
            position: absolute;
            top: 0px;
            right: 60px;
        }
        .dislike {
            position: absolute;
            top: 0px;
            right: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Define a dictionary to store the number of upvotes and downvotes for each message
if 'votes' not in st.session_state:
    st.session_state.votes = {}

# Display messages with appropriate CSS class and upvote/downvote buttons
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message = st.session_state['generated'][i]
            st.markdown(f"<div class='you'>🧑‍🎓: {st.session_state['past'][i]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='waam'>🏫: {message}</div>", unsafe_allow_html=True)
            if ret:
                st.write(ret)
                # Not sure if this is what we want
                del(ret)

            if message not in st.session_state.votes:
                st.session_state.votes[message] = [0, 0]
            upvote_button = st.button(f"👍 ({st.session_state.votes[message][0]})", key=f"upvote_{i}")
            downvote_button = st.button(f"👎 ({st.session_state.votes[message][1]})", key=f"downvote_{i}")
            if upvote_button:
                st.session_state.votes[message][0] += 1
            elif downvote_button:
                st.session_state.votes[message][1] += 1
