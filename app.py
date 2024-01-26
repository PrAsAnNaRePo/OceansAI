import os
import requests
from dotenv import load_dotenv
import streamlit as st
import json
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ.get("TOGETHER_API_KEY"),
  base_url='https://api.together.xyz',
)

def get_search_results(query:list):
    search_results = []
    for q in query:
        url = "https://google.serper.dev/search"
        payload = json.dumps([
        {
            "q": q,
            "num": 5
        },
        ])
        headers = {
        'X-API-KEY': os.environ.get("SERPER_API_KEY"),
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.json())
        search_results.append(response.json()[0]['organic'][0] if len(response.json()[0]['organic']) > 0 else response.json()[0]['topStories'][0])

    return search_results


st.title("Type your title; get some sources")

query = st.text_area("Type your text here")

if st.button('submit') and query is not None:
    msg = [
        {"role": "system", "content": "You are a AI Assistant.\nGiven a query, you will return a list of search quries that you think are relevant to the query. Search for Books, Movies, Series, Articles, entreprenuers, Personalities, etc for the user query.\nUse JSON to format your response. Generate only 5 to 7 query, make sure you are using different queries, but related."},
        {"role": "user", "content": f"""Here is the syntax for the JSON response:
{{
    "serach_queries": [query1, query2, query3, ...]
}}

Here is the given user query: {query}"""}
    ]

    with st.spinner():
        completion = client.chat.completions.create(
            model="openchat/openchat-3.5-1210",
            messages=msg,
            stream=False
        )

    print(completion.choices[0].message.content)
    json_response = json.loads(completion.choices[0].message.content)
    queris = json_response["search_queries"]
    print(queris)
    st.write("searching for ", queris)
    with st.spinner(text="Searching for sources..."):
        search_results = get_search_results(queris)
    print(search_results)

    msg = [
        {"role": "system", "content": "Given a query and search results, your goal is to return a well-organized list of sources relevant to the query. Categorize the sources under different headings such as Books, Movies, Series, Articles, Entrepreneurs, Personalities, etc as many heading you want. Also don't include any links in these headings. Write content under each heading without including any links. Additionally, create a 'References' section at the end to include all the links and references related to the query. Ensure that links are only placed in the 'References' section and not under other headings. Use markdown format."},
        {"role": "user", "content": f"search results: {search_results}\nuser query: {query}"}
    ]

    with st.spinner("generating sources for you..."):
        completion = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=msg,
            stream=False
        )

    st.write(completion.choices[0].message.content)