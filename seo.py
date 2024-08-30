import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging

import requests
from bs4 import BeautifulSoup
import textstat
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow warnings

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] ="key"  # Replace with your actual API key

def advanced_seo_optimizer(url):
    try:
        # Fetch and parse the webpage
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text()
        
        # 1. Content Quality Analysis
        readability_score = textstat.flesch_reading_ease(text_content)
        
        # 2. Keyword Extraction using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
        tfidf_matrix = vectorizer.fit_transform([text_content])
        feature_names = vectorizer.get_feature_names_out()
        important_keywords = [str(feature_names[i]) for i in tfidf_matrix.sum(axis=0).argsort()[0, -10:][0]]
        
        # 3. Semantic Analysis using Universal Sentence Encoder
        embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        embeddings = embed([text_content])
        
        # 4. Content Suggestions using LangChain and OpenAI
        template = """
        Based on the following information about a webpage, provide 3-5 specific suggestions to improve its SEO:
        
        URL: {url}
        Readability Score: {readability_score}
        Important Keywords: {keywords}
        
        Please format your response as a bullet point list.
        """
        
        prompt = PromptTemplate(
            input_variables=["url", "readability_score", "keywords"],
            template=template,
        )
        
        llm = OpenAI(temperature=0.7)
        chain = prompt | llm | StrOutputParser()
        print("\nimportant_keywords",important_keywords)
        suggestions = chain.invoke({
            "url": url,
            "readability_score": readability_score,
            "keywords": ", ".join(important_keywords)
        })
        
        # 5. Check Google Indexing Status
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(f"https://www.google.com/search?q=site:{url}")
        indexed = "No results found" not in driver.page_source
        driver.quit()
        
        # Prepare and print the report
        print(f"\nAdvanced SEO Analysis for: {url}")
        print(f"\nReadability Score: {readability_score:.2f}")
        print(f"\nImportant Keywords: {', '.join(important_keywords)}")
        print(f"\nGoogle Indexing Status: {'Indexed' if indexed else 'Not Indexed'}")
        print(f"\nSEO Improvement Suggestions:")
        print(suggestions)
        
        return {
            "url": url,
            "readability_score": readability_score,
            "important_keywords": important_keywords,
            "indexed": indexed,
            "suggestions": suggestions
        }
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Example usage
url = "https://www.avathi.com/experience/pondicherry-packages/1454"
result = advanced_seo_optimizer(url)
print(result)
# if result:
#     # You can further process or store the results as needed
#     pass