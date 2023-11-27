import openai
import os
import json
import requests
import fitz #pip install pymupdf
from dotenv import load_dotenv, find_dotenv
from csv import DictWriter
from bs4 import BeautifulSoup #pip install beautifulsoup4

positive_negative_sentiment_analysis_prompt = """
    Perform basic sentiment analysis on a piece of provided text. 
    Provide following in JSON format: an appropriate title of the article, the classification of the text as positive/negative/neutral, 
    a summary of the article which is at most 3 sentences, and the reasoning for the classification which is at most three sentences. 
    Let the features be labeled as title, classification, summary, and reasoning. 
    """

# this one may be limited by the model's intelliegence, it reguarly told me that criticizing
# a left-leaning political party was a sign of the article being left-leaning
# and vice versa for criticism of a right-leaning party
# it seems to make its decision based on which 
# maybe some more prompt engineering will get it in line
political_sentiment_analysis_prompt = """
    Perform political sentiment analysis with specific attention to praise and critcism on a piece of provided text. 
    Provide following in JSON format: an appropriate title of the article, the classification of the text as being right-leaning/center/left-leaning, 
    a summary of the article which is at most 3 sentences, and the reasoning for the classification which is at most three sentences. 
    Let the features be labeled as title, classification, summary, and reasoning.     
    """
    
sarcasm_irony_sentiment_analysis_prompt = """
    Perform sentiment analysis on a piece of provided text, looking for signs of intentional sarcasm and or irony. 
    Provide following in JSON format: an appropriate title of the article, the ranking of the text from 0-10 with 0 indicating no sarcasm and 10 indicating extreme sarcasm, 
    a summary of the article which is at most 3 sentences, and the reasoning for the classification which is at most three sentences. 
    Let the features be labeled as title, classification, summary, and reasoning.     
    """

fiction_nonfiction_sentiment_analysis_prompt = """
    Perform sentiment analysis on a piece of provided text, looking to classify the work as either fiction or non-fiction.
    Provide following in JSON format: an appropriate title of the article, the classification of the text as being fiction or non-fiction, 
    a summary of the article which is at most 3 sentences, and the reasoning for the classification which is at most three sentences. 
    Let the features be labeled as title, classification, summary, and reasoning. 
    """

historical_era_sentiment_analysis_prompt = """
    Perform sentiment analysis on a piece of provided text, looking to classify the historical era the text was written during.
    Provide following in JSON format: an appropriate title of the article, the classification of the historical era the text was written during, 
    a summary of the article which is at most 3 sentences, and the reasoning for the classification which is at most three sentences. 
    Let the features be labeled as title, classification, summary, and reasoning. 
    """
geographic_area_sentiment_analysis_prompt = """
    Perform sentiment analysis on a piece of provided text, looking to classify the geographic area the text was written.
    Provide following in JSON format: an appropriate title of the article, the classification of the geographic area the text was written, 
    a summary of the article which is at most 3 sentences, and the reasoning for the classification which is at most three sentences. 
    Let the features be labeled as title, classification, summary, and reasoning. 
    """
    
prompt_map = {
              "Positive/Negative": positive_negative_sentiment_analysis_prompt,
              "Political" : political_sentiment_analysis_prompt,
              "Sarcasm" : sarcasm_irony_sentiment_analysis_prompt,
              "Fiction/Non-Fiction" : fiction_nonfiction_sentiment_analysis_prompt,
              "Historical" : historical_era_sentiment_analysis_prompt,
              "Geographic" : geographic_area_sentiment_analysis_prompt,
             }

def get_api_key():
    _ = load_dotenv(find_dotenv())  # read local .env file
    openai.api_key = os.getenv('OPENAI_API_KEY')


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content


def get_user_input():
    """Basic command line interface. Returns the text specified by the user."""
    print("To read a custom file add it to the Data directory.")
    print("Files in the Data Directory: ")

    files = os.listdir("./Data")
    file_choice = len(files)+1
    while (file_choice == len(files)+1):
        # List all avalible files
        files = os.listdir("./Data")
        for file_num in range(len(files)):
            print(str(file_num + 1) + ". " + files[file_num])
        print(str(len(files)+1) + ". Refresh avalible files")

        file_choice = int(
            input("Enter the number of the file you would like to read / Enter 100 to submit a URL: "))
    
    if(file_choice == 100):
        input_file = input("Enter the URL: ")
    else:
        input_file = files[file_choice-1]

    # Handling Inputs #     
    if(input_file.endswith(".pdf")):
        text = read_pdf_file(input_file)
    elif(input_file.endswith(".txt")):
        text = read_txt_file(input_file)
    elif(input_file.startswith("https://")):
        text = read_url(input_file)
    elif(input_file.endswith(".html")):
        text = read_html_file(input_file)
     
    print("\n")
    
    analysis_types = list(prompt_map.keys())
    
    analysis_choice = len(analysis_types)+1
    while (analysis_choice == len(analysis_types)+1):

        for analysis_num in range(0, len(analysis_types)):
            
            print(str(analysis_num + 1) + "." + analysis_types[analysis_num])
            
        analysis_choice = int(
            input("Enter the number of the analysis type you would like to apply:")
        )
        
    analysis_type = analysis_types[analysis_choice-1]
    
    return (text, analysis_type)

def read_txt_file(file_name):
    f = open("./Data/"+file_name, "r", encoding="utf8")
    return f.read()

def read_pdf_file(file_name):
    doc = fitz.open("./Data/"+file_name)
    for page in doc:
        text = page.get_text().encode("utf8") 
    return text

def read_html_file(file_name):
    try:
        with open("./Data/"+file_name, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator=' ')
            return text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    
def append_to_csv(response):
    dict_to_append = json.loads(response)

    features = ["title", "classification", "summary", "reasoning"]

    if os.path.exists("output.csv"):
        csv_file = open("output.csv", "a", newline="")
        dict_writer = DictWriter(csv_file, fieldnames=features)
        dict_writer.writerow(dict_to_append)
        csv_file.close()
    else:
        csv_file = open("output.csv", "a", newline="")
        dict_writer = DictWriter(csv_file, fieldnames=features)
        dict_writer.writeheader()
        dict_writer.writerow(dict_to_append)
        csv_file.close()


def run_analysis():   
    
    (text, analysis_type) = get_user_input()
    
    prompt = ""
    
    if analysis_type in prompt_map.keys():
        
        prompt = prompt_map[analysis_type] + f"Text: ```{text}```"
        
    else:
        
        print("invalid analysis type")
        return

    print("Running analysis...")
    response = get_completion(prompt)
    print(response)
    append_to_csv(response)
