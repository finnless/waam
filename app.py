import openai
import streamlit as st
import pandas as pd

# Setting page title and header
st.set_page_config(page_icon=":bulb:", page_title="WAAM-GPT")
st.markdown("<div style='text-align: center;'><h1 style='display: inline-block;'> 💡WAAM-GPT</h1><h5 style='display: inline-block; margin-left: 10px; color: gray;'>homework help</h5></div>", unsafe_allow_html=True)

# Set org ID and API key
openai.organization = st.secrets["openai_org"]
openai.api_key = st.secrets["openai_key"]

system_prompt = "You are a waam, a helpful large language model STEM tutor created during the 2023 5C Hackathon. You help users learn quantitative skills by guiding them through concepts and practice problems step by step instead of immediately giving away the final answer. Never give a student the direct answer. Always use markdown for your responses. Always render equations using LaTeX."

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

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": system_prompt}
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
model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model names to OpenAI model IDs
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
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
    # response = completion.choices[0].message.content
     # print("response: ", response)
    # json_response = json.loads(response)

    json_response = {
    "message": "A normal distribution, also known as Gaussian distribution, is a continuous probability distribution that has a bell-shaped curve. It is symmetric around its mean ($\\mu$), and its shape is determined by its mean and standard deviation ($\\sigma$). The majority of the data in a normal distribution lies within a few standard deviations from the mean. Specifically, about 68% of the data is within 1 standard deviation, 95% is within 2 standard deviations, and 99.7% is within 3 standard deviations.\n\nThe probability density function (PDF) of a normal distribution is given by:\n\n$$f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{\\frac{-(x-\\mu)^2}{2\\sigma^2}}$$\n\nHere's a plot of a normal distribution with mean $\\mu = 0$ and standard deviation $\\sigma = 1$ (a standard normal distribution):",
    "python": "import numpy as np\nimport matplotlib.pyplot as plt\nfrom scipy.stats import norm\n\nx = np.linspace(-5, 5, 1000)\nmu = 0\nsigma = 1\n\ny = norm.pdf(x, mu, sigma)\n\nplt.plot(x, y)\nplt.xlabel('x')\nplt.ylabel('f(x)')\nplt.title('Normal Distribution: $\\mu=0$, $\\sigma=1$')\nplt.grid()\n\nret = plt.gcf()"
    }
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
            exec(json_output["python"])

# Define CSS styles for messages
st.markdown("""
    <style>
        .you {
            background-color: #d3d3d3;
        }
        .waam {
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# Display messages with appropriate CSS class
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            st.markdown(f"<div class='you'>🧑‍🎓: {st.session_state['past'][i]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='waam'>🏫: {st.session_state['generated'][i]}</div>", unsafe_allow_html=True)
            st.write(ret)
