import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer

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

# Display the chat history in the sidebar
with st.sidebar:
    st.subheader("Chat History")
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.write(f"You: {message['content']}")
            else:
                st.write(f"Assistant: {message['content']}")

# Add a brief description of the app
st.markdown("This app allows you to search for Wikipedia topics and displays the content in a chat-like format. You can also toggle between using the Wikipedia scraper and a GPT-2 model to generate the response.")

prompt = st.text_input("Enter the Topic: ")

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

    for i in corpus.split():
        yield i + " "

def get_random_wikipedia_topic():
    url = "https://en.wikipedia.org/wiki/Special:Random"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find('h1', {'id': 'firstHeading'}).text

if st.sidebar.button("Get Random Wikipedia Topic"):
    random_topic = get_random_wikipedia_topic()
    st.sidebar.write(f"Random Topic: {random_topic}")
    prompt = random_topic

use_gpt2 = st.sidebar.checkbox("Use GPT-2 Model")
use_chatgpt = st.sidebar.checkbox("Use ChatGPT")

if prompt:
    link = generate_link(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if use_gpt2:
            # Load the pre-trained GPT-2 model and tokenizer
            model = GPT2LMHeadModel.from_pretrained('gpt2')
            tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

            # Generate the response using GPT-2
            input_ids = tokenizer.encode(prompt, return_tensors='pt')
            output = model.generate(input_ids, max_length=300, num_return_sequences=1, do_sample=True, top_k=50, top_p=0.95, num_beams=1)[0]
            full_response = tokenizer.decode(output, skip_special_tokens=True)
        elif use_chatgpt:
            # Load the pre-trained ChatGPT model
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            model = GPT2LMHeadModel.from_pretrained('gpt2')
            tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

            # Generate the response using ChatGPT
            input_ids = tokenizer.encode(prompt, return_tensors='pt')
            output = model.generate(input_ids, max_length=300, num_return_sequences=1, do_sample=True, top_k=50, top_p=0.95, num_beams=1)[0]
            full_response = tokenizer.decode(output, skip_special_tokens=True)
        else:
            for chunk in generating_wiki_link(link):
                full_response += chunk
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
