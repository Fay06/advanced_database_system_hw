# COMS6111 - Project2


### A clear description of how to run your program. Note that your project must run in a Google Cloud VM set up exactly following our instructions (but with more memory, etc. for this project as indicated above). Provide all commands necessary to install the required software and dependencies for your program.

install related package at first:

1. pip3 install --upgrade google-api-python-client
2. pip3 install beautifulsoup4
3. pip3 install -U spacy
4. pip3 install openai
5. python3 -m spacy download en_core_web_lg
6. pip3 install -r requirements.txt
7. bash download_finetuned.sh

run the command:

9. python3 project2.py -spanbert|-gpt3 {google api key} {google engine id} {openai secret key} {r} {t} {q} {k}

### A clear description of the internal design of your project, explaining the general structure of your code (i.e., what its main high-level components are and what they do), as well as acknowledging and describing all external libraries that you use in your code

google_search: search on Google

spanbert_helper: use SpanBERT

gpt_helper: use OpenAI GPT-3's API

main: main function

### A detailed description of how you carried out Step 3 in the "Description" section above

1. I use a set to collect all URL: If I find it is in the set, I will skip it; otherwise, I will add it into the set 
2. I use request.get to retrieve the corresponding webpage, when I catch an error, I will skip it
3. I use beautiful soup to extract the actual plain text from the webpage and clean it
4. I limit the length of plain text to 10000
5. I use spacy to split the text into sentences and extract entities
6. I call spanbert_helper if -spanbert is specified; I call gpt_helper if -gpt3 is specified; otherwise, I will raise an error
7. For the spanbert_helper, I change the create_entity_pairs given by professor to meet the spanbert requirement, and I use the create_entity_pairs to get the entity pairs; For the gpt_helper, I change the create_entity_pairs given by professor to follow the gpt logic, and I use the create_entity_pairs to get the entity pairs.

