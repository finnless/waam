import openai
import streamlit as st
import json

# Setting page title and header
st.set_page_config(page_title="waam", page_icon=":robot_face:")

# Set org ID and API key
openai.organization = st.secrets["openai_org"]
openai.api_key = st.secrets["openai_key"]

system_prompt = "You are a waam, a helpful large language model STEM tutor created during the 2023 5C Hackathon. \
You help users learn quantitative skills by guiding them through concepts and practice problems step by step instead of \
immediately giving away the final answer. Never give a student the direct answer. \
Always use markdown for your responses. Always render equations using LaTeX.\
When necessary, create graphs and plots with python libraries to help the student visualize a concept.\
Your response should have a \"message\" and a \"python\" component.  The \"message\" component should have \
any explanatory text and markdown.  The \"python\" component should have the the python code \
that will produce the graph or plot.  The response should strictly be in json format, as follows: \
{\"message\" : // insert your message here, \"python\": // insert your python code here}" 

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
st.sidebar.title("Sidebar")
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
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

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

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        json_output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(json_output["message"])

        if json_output["python"] != "":
            exec(json_output["python"])
        
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            st.markdown(f"**You**: {st.session_state['past'][i]}", unsafe_allow_html=True)
            st.markdown(f"**waam**: {st.session_state['generated'][i]}", unsafe_allow_html=True)
            st.write(ret)
            st.write(
                f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
