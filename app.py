import openai
import streamlit as st
import pandas as pd
import PyPDF2


def pdf_reader(file):
    """Reads text from a PDF file"""
    try:
        # Read the uploaded file using PyPDF2
        pdf = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(pdf.pages)):
            text += pdf.pages[page].extract_text()

        return text
    except Exception as e:
        # Handle any exceptions that may occur
        print("Error reading PDF file:", e)
        return None


# Setting page title and header
st.set_page_config(page_icon=":bulb:", page_title="WAAM-GPT")
st.markdown("<div style='text-align: center;'><h1 style='display: inline-block;'> 💡WAAM-GPT</h1><h5 style='display: inline-block; margin-left: 10px; color: gray;'>homework help</h5></div>", unsafe_allow_html=True)

# Set org ID and API key
openai.organization = st.secrets["openai_org"]
openai.api_key = st.secrets["openai_key"]

system_prompt = """
You are a waam, a helpful large language model STEM tutor created during the 2023 5C Hackathon. You help users learn quantitative skills by guiding them through concepts and practice problems step by step instead of immediately giving away the final answer. Always use markdown for your responses. Always render equations using LaTeX.
Whenever possible, create graphical visualizations to help students understand concepts. Use the plotly python module whenever possible. The last line should always set the variable ret to an object representing the graph or plot. If you are creating a visualization, create a codeblock with "figure" after the backticks like this:

```figure
import plotly.graph_objects as go
fig = go.Figure()
# Represent 1 as a dot
fig.add_trace(go.Scatter(x=[1], y=[1], mode='markers', marker=dict(size=10), name='1'))
# Represent another 1 as a dot
fig.add_trace(go.Scatter(x=[2], y=[1], mode='markers', marker=dict(size=10), name='1'))
# Configure the layout
fig.update_layout(title='Visual Proof of 1 + 1 = 2', xaxis_title='Number of Dots', yaxis_title='', showlegend=False)
# Set ret to the graph
ret = fig
```
"""

# Autogenerate message
st.write("Welcome to WAAM! We are here to help you do well in STEM subjects at school")

# Create some data
data = {
    'Mathematics': ['Linear Algebra', 'Calculus I', 'Chaos Theory'],
    'Statistics': ['What is a normal distribution?', 'Chi-Square Distribution', 'Linear Regression'],
    'Limitations': ['May occasionally generate incorrect information', 'Limited knowledge of world and events after 2021', 'still in beta version']
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


def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    print("response: ", response)
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens


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
        submit_button = st.form_submit_button(label='⏩')

        # create a file uploader for PDFs
        pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

        # if a PDF file is uploaded, extract its text
        if pdf_file is not None:
            user_input = pdf_reader(pdf_file)

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)

        output_parts = []
        if '```figure' in output:
            print('DEBUG: FIGURE FOUND')
            begin_figure_split = output.split('```figure')
            output_parts.append(begin_figure_split[0])

            end_figure_split = begin_figure_split[1].split('```')
            figure = end_figure_split[0]
            # label as figure
            figure = 'figure\n' + figure
            output_parts.append(figure)
            # Response after figure
            output_parts.append(end_figure_split[1])
            # TODO THIS IS PROBABLY BROKEN FOR OUTPUTS WITH MULTIPLE CODE BLOCKS
        else:
            output_parts.append(output)

        st.session_state['generated'].append(output_parts)
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
            question = st.session_state['past'][i]
            st.markdown(f"<div class='you'>🧑‍🎓: {question}</div>", unsafe_allow_html=True)
            for m in message:
                print(m[:6])
                if m[:6] == 'figure':
                    print('DEBUG: EXECING FIGURE')
                    # exec and render
                    figure = m[6:]
                    try:
                        exec(figure)
                        st.write(ret)
                        ret = None
                    except Exception as e:
                        st.exception(f'Generated python code failed:\n{e}')
                else:
                    st.markdown(f"<div class='waam'>🏫: {m}</div>", unsafe_allow_html=True)

            if question not in st.session_state.votes:
                st.session_state.votes[question] = [0, 0]
            upvote_button = st.button(f"👍 ({st.session_state.votes[question][0]})", key=f"upvote_{i}")
            downvote_button = st.button(f"👎 ({st.session_state.votes[question][1]})", key=f"downvote_{i}")
            if upvote_button:
                st.session_state.votes[question][0] += 1
            elif downvote_button:
                st.session_state.votes[question][1] += 1
