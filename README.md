# Introduction to this Project!
The goal of this project is to get myself familiar with the openAI API, and use chatgpt as a very basic setiment analysis tool. Currently the model either creates or appends to a csv file with the name "output.csv". This allows the user to save their previous runs of the model. The input for this model is a txt file added to the data directory. The features this model provides are a title for the text document, a classification as either positive/negative/neutral in terms of sentiment, a three sentence or less summary of the document, and chatGPT's reasoning for the classification, which is also three sentences or less. 

## API Key
This program uses a .env file to save and load the users API key. In order to use this program you must create a .env file which includes
OPENAI_API_KEY= *YOUR KEY HERE*

## User Input
Currently the model uses a very basic command line interface displaying all the files in the Data directory. From here the user can select the file they wish the model to analyze, assuming again the file is in the Data directory. 

## Why use this program over chatGPT's web interface?
This program has a few benefits which the web based GUI for chatGPT does not support. With this program you are able to run multiple classifications quickly and efficiently, with the output being stored neatly in a CSV file. If a user wished to do this with openAI's web interface the user would have to manually save each output. The user would also have to manually upload the text document, something that is much more efficient in this program. You are also able to adjust and tune chatGPT to reach your desired output, such as modifying the temperature variable.