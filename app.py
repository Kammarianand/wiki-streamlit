import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="WikiStream", page_icon="ℹ️", layout="wide")

st.title("Wiki-Fetch")

# Initialize session state
if 'stop_generation' not in st.session_state:
    st.session_state.stop_generation = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def magic():
    st.toast("woah......!🎉")
    time.sleep(0.1)
    st.toast("This is not chatGPT, info is from wiki😁")
    time.sleep(0.2)
    st.toast("you can click on stop button👀")

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
            if 'en.wikipedia.org' in link:
                actual_link = link[7:].split('&')[0]
                return scraping_data(actual_link)
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
        corpus = corpus.replace('['+str(i)+']', " ")
    
    for i in corpus.split():
        if st.session_state.stop_generation:
            break
        yield i + " "
        time.sleep(0.2)

# Chat UI
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input area and Stop button
col1, col2 = st.columns([5, 1])
with col1:
    prompt = st.chat_input("Enter the Topic:")
with col2:
    stop_button = st.button("Stop")

if stop_button:
    st.session_state.stop_generation = True

if prompt:
    st.session_state.stop_generation = False
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        magic()
        link = generate_link(prompt)
        if link:
            for chunk in generating_wiki_link(link):
                if st.session_state.stop_generation:
                    break
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# Reset Chat button
if st.button("Reset Chat"):
    st.session_state.chat_history = []
    st.session_state.stop_generation = False
    st.experimental_rerun()
    
