import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random

st.set_page_config(page_title="WikiStream", page_icon="ℹ")

st.title("Wiki-Fetch")


st.sidebar.title("Options")


theme = st.sidebar.selectbox("Choose a theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {
        background-color: #2b2b2b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


if 'messages' not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Enter the Topic: ")

def generate_link(prompt):
    if prompt:
        return "https://www.google.com/search?q=" + prompt.replace(" ", "+") + "+wiki"
    else:
        return None

def generating_wiki_link(link):
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')
    for sp in soup.find_all("div"):
        try:
            link = sp.find('a').get('href')
            if ('en.wikipedia.org' in link):
                actua_link = link[7:].split('&')[0]
                return scraping_data(actua_link)
                break
        except:
            pass

def scraping_data(link):
    actual_link = link
    res = requests.get(actual_link)
    soup = BeautifulSoup(res.text, 'html.parser')
    corpus = ""
    for i in soup.find_all('p'):
        corpus += i.text
        corpus += '\n'
    corpus = corpus.strip()
    for i in range(1, 500):
        corpus = corpus.replace('[' + str(i) + ']', " ")

    speed = st.sidebar.slider("Text Speed", 0.1, 1.0, 0.2, 0.1)
    
    for i in corpus.split():
        yield i + " "
        time.sleep(speed)


def get_random_wikipedia_topic():
    url = "https://en.wikipedia.org/wiki/Special:Random"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find('h1', {'id': 'firstHeading'}).text

if st.sidebar.button("Get Random Wikipedia Topic"):
    random_topic = get_random_wikipedia_topic()
    st.sidebar.write(f"Random Topic: {random_topic}")
    prompt = random_topic

if prompt:
    link = generate_link(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in generating_wiki_link(link):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()


if st.sidebar.button("Summarize Last Response"):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_response = st.session_state.messages[-1]["content"]
        summary = " ".join(last_response.split()[:50]) + "..."
        st.sidebar.markdown("### Summary")
        st.sidebar.write(summary)
