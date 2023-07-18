# COMS6111 Project 1

#### How To Run
* install related package at first:
  * pip3 install --upgrade setuptools wheel pip
  * pip3 install scikit-learn
* run the command:
  * python3 main.py <google api key> <google engine id> <precision> <query>

#### Internal Design
* def google_search(query, google_api_key, google_engine_id): 
  * search on Google
* def UI(query, google_api_key, google_engine_id, precision, first_iter=False): 
  * user interface
* def Rocchio(q_vectors, relevant_vectors, non_relevant_vectors, query, words):
  * rocchio algorithm
* def main(): 
  * main function
  
#### Query-modification Method
* Receive a user query as input , which is simply a list of words
* Retrieve the top-10 results for the query from Google, using the Google Custom Search API
* Then user can mark all the webpages that are relevant to the intended meaning of the query among the top-10 results

