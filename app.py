import streamlit as st 
import requests 
from bs4 import BeautifulSoup 
import time 

st.set_page_config(page_title="WikiStream", page_icon="ℹ️") 

st.title("Wiki-Fetch")

# Add a stop button and handle its state
if 'stop_generation' not in st.session_state:
    st.session_state.stop_generation = False

def stop_content():
    st.session_state.stop_generation = True

def reset_stop_state():
    st.session_state.stop_generation = False

# Include the stop button next to chat input
col1, col2 = st.columns([5, 1])
with col1:
    prompt = st.chat_input("Enter the Topic: ")

with col2:
    st.button("Stop", on_click=stop_content)

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

link = generate_link(prompt) 

def generating_wiki_link(link): 
    res = requests.get(link) 
    soup = BeautifulSoup(res.text,'html.parser') 
    for sp in soup.find_all("div"): 
        try: 
            link = sp.find('a').get('href') 
            if('en.wikipedia.org' in link): 
                actua_link = link[7:].split('&')[0] 
                return scraping_data(actua_link) 
                break 
        except: 
            pass 

def scraping_data(link): 
    actual_link = link 
    res = requests.get(actual_link) 
    soup = BeautifulSoup(res.text,'html.parser') 
    corpus = "" 
    for i in soup.find_all('p'): 
        corpus += i.text 
        corpus += '\n' 
    corpus = corpus.strip() 
    for i in range(1,500): 
        corpus = corpus.replace('['+str(i)+']'," ") 

    for i in corpus.split(): 
        if st.session_state.stop_generation:
            st.write("Content generation stopped by user.")
            break
        yield i + " " 
        time.sleep(0.2) 

if link: 
    with st.container(): 
        with st.chat_message('assistant'): 
            magic() 
            for word in generating_wiki_link(link):
                st.write(word, end='')  # Continue printing words
            reset_stop_state()  # Reset stop state for next time
