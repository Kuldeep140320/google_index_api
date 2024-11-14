import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging

import requests
from bs4 import BeautifulSoup
import textstat
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import re

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # Replace with your actual API key

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
        
        # 3. Semantic Analysis using OpenAI Embeddings
        embeddings_model = OpenAIEmbeddings()
        text_embedding = embeddings_model.embed_query(text_content)
        
        # Example use of embeddings: Calculate similarity with a target keyword
        target_keyword = "travel"
        target_embedding = embeddings_model.embed_query(target_keyword)
        similarity = np.dot(text_embedding, target_embedding) / (np.linalg.norm(text_embedding) * np.linalg.norm(target_embedding))
        
        # 4. Content Suggestions using LangChain and OpenAI
        template = """
        Based on the following information about a webpage, provide 3-5 specific suggestions to improve its SEO:
        
        URL: {url}
        Readability Score: {readability_score}
        Important Keywords: {keywords}
        Similarity with 'travel': {similarity}
        
        For each suggestion, provide:
        1. The current state
        2. The suggested improvement
        3. How this improvement would affect the SEO metrics
        
        Please format your response as a bullet point list.
        """
        
        prompt = PromptTemplate(
            input_variables=["url", "readability_score", "keywords", "similarity"],
            template=template,
        )
        
        llm = OpenAI(temperature=0.7)
        chain = prompt | llm | StrOutputParser()
        
        suggestions = chain.invoke({
            "url": url,
            "readability_score": readability_score,
            "keywords": ", ".join(important_keywords),
            "similarity": f"{similarity:.4f}"
        })
        
        # 5. Check Google Indexing Status
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(f"https://www.google.com/search?q=site:{url}")
        indexed = "No results found" not in driver.page_source
        driver.quit()
        
        # 6. Simulate improvements
        improved_url = "https://www.avathi.com/guide/goa/5"
        improved_text_content = simulate_improved_content(text_content, important_keywords, target_keyword)
        improved_readability_score = textstat.flesch_reading_ease(improved_text_content)
        improved_tfidf_matrix = vectorizer.transform([improved_text_content])
        improved_important_keywords = [str(feature_names[i]) for i in improved_tfidf_matrix.sum(axis=0).argsort()[0, -10:][0]]
        improved_text_embedding = embeddings_model.embed_query(improved_text_content)
        improved_similarity = np.dot(improved_text_embedding, target_embedding) / (np.linalg.norm(improved_text_embedding) * np.linalg.norm(target_embedding))
        
        # Prepare and print the report
        print(f"\nAdvanced SEO Analysis for: {url}")
        print(f"\nCurrent Metrics:")
        print(f"Readability Score: {readability_score:.2f}")
        print(f"Important Keywords: {', '.join(important_keywords)}")
        print(f"Similarity with 'travel': {similarity:.4f}")
        print(f"Google Indexing Status: {'Indexed' if indexed else 'Not Indexed'}")
        
        print(f"\nImproved Metrics:")
        print(f"Improved URL: {improved_url}")
        print(f"Improved Readability Score: {improved_readability_score:.2f}")
        print(f"Improved Important Keywords: {', '.join(improved_important_keywords)}")
        print(f"Improved Similarity with 'travel': {improved_similarity:.4f}")
        
        print(f"\nSEO Improvement Suggestions:")
        print(suggestions)
        
        return {
            "current_url": url,
            "current_readability_score": readability_score,
            "current_important_keywords": important_keywords,
            "current_similarity": similarity,
            "current_indexed": indexed,
            "improved_url": improved_url,
            "improved_readability_score": improved_readability_score,
            "improved_important_keywords": improved_important_keywords,
            "improved_similarity": improved_similarity,
            "suggestions": suggestions
        }
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def simulate_improved_content(original_content, keywords, target_keyword):
    # This is a simplified simulation. In a real scenario, you'd want a more sophisticated content improvement method.
    improved_content = original_content
    
    # Add keywords and related terms
    for keyword in keywords:
        improved_content += f" {keyword}"
    
    improved_content += f" {target_keyword} adventure explore vacation"
    
    # Simplify sentences (very basic simulation)
    sentences = re.split(r'(?<=[.!?]) +', improved_content)
    simplified_sentences = [s[:100] if len(s) > 120 else s for s in sentences]  # Shorten long sentences
    improved_content = ' '.join(simplified_sentences)
    
    return improved_content

# Example usage
url = "https://www.avathi.com/guide/goa/5"
result = advanced_seo_optimizer(url)

if result:
    # You can further process or store the results as needed
    pass