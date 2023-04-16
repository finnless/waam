# waam
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://finnless-waam-app-xf6cqs.streamlit.app/)
[![DevPost](https://img.shields.io/badge/DevPost-waam-blue?logo=DevPost)](https://devpost.com/software/waam)

Have you ever wanted help but you do not know who to go to? Generally, tutors do not allow students to search up homework problems on google or ask peers because they want students to think through what they are doing. You might have wanted to go to school approved tutoring places such as CMC’s QCL or Pomona’s QSC, but they might not be available on weekends when you actually do all your homework. 

We sympathize with students so we want to build a platform that can help students with homework anytime they want help. Tutors will be more willing to approve this platform because it will never give homework solutions. What it will do instead is that It will clarify concepts that students are struggling with or provide hints for homework problems. 

Basically students can ask a question on the chat box in any area of study such as Math, Physics, Economics, Statistics etc. As long as the question is not about providing a solution, GPT-4 will generate an answer that will include visualizations. If a student asks for a solution, GPT-4 will politely say no and give the students additional ways it could help. 

## Installation

 - Clone the repo
 - Install requirements by running `$ pip install -r requirements.txt`
 - Modify the [Streamlit Secrets file](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management) `.streamlit/secrets.toml` to include your OpenAI API key and organization id.
 - Run the app with the command `$ streamlit run app.py`
