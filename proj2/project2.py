__author_1__ = "Yufei Liu, yl5099"
__author_2__ = "Yipeng Geng, yg2913"

import sys
from googleapiclient.discovery import build
import spacy
from spanbert import SpanBERT
import requests
from bs4 import BeautifulSoup
import spacy_help_functions
import openai
import re

spacy2bert = {"ORG": "ORGANIZATION", "PERSON": "PERSON", "GPE": "LOCATION", "LOC": "LOCATION"}
bert2spacy = {"ORGANIZATION": "ORG", "PERSON": "PERSON", "LOCATION": "LOC", "CITY": "GPE", "COUNTRY": "GPE",
              "STATE_OR_PROVINCE": "GPE"}
relations = {'1': 'Schools_Attended', '2': 'Work_For', '3': 'Live_In', '4': 'Top_Member_Employees'}
r2required_entities = {'1': ["PERSON", "ORGANIZATION"], '2': ["PERSON", "ORGANIZATION"],
                       '3': ["PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"],
                       '4': ["ORGANIZATION", "PERSON"]}
gpt_example = {'1': "[relationship: Schools_Attended; subject: Jeff Bezos; object: Princeton University]",
               '2': "[relationship: Work_For; subject: Alec Radford; object: OpenAI]",
               '3': "[relationship: Live_In; subject: Mariah Carey; object: New York City]",
               '4': "[relationship: Top_Member_Employees; subject: Jensen Huang; object: Nvidia]"}


def google_search(query, google_api_key, google_engine_id):
    service = build(
        "customsearch", "v1", developerKey=google_api_key
    )

    res = (
        service.cse()
            .list(
            q=query,
            cx=google_engine_id,
        )
            .execute()
    )
    return res


def spanbert_helper(X, tuple_added, tuple_total, spanbert_model, sent, required_entities, r, t):
    extracted_entity_pairs = spacy_help_functions.create_entity_pairs(sent, required_entities)
    # print(extracted_entity_pairs)
    annotated = 0
    if len(extracted_entity_pairs) > 0:
        examples = []
        for ep in extracted_entity_pairs:
            entity1 = ep[1][1]
            entity2 = ep[2][1]
            if entity1 in required_entities[0] and entity2 in required_entities[1:]:
                examples.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})
            elif entity2 in required_entities[0] and entity1 in required_entities[1:]:
                examples.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})
        if len(examples) > 0:
            annotated = 1
            preds = spanbert_model.predict(examples)
            for ex, pred in list(zip(examples, preds)):
                relation = pred[0]
                confidence = pred[1]
                subj = ex["subj"][0]
                obj = ex["obj"][0]
                if relation == 'no_relation':
                    continue
                print("                === Extracted Relation ===")
                print("                Input tokens:", ex["tokens"])
                print(
                    "                Output Confidence: {} ; Subject: {} ; Object: {} ;".format(confidence, subj, obj))

                new_tuple = (subj, obj)
                tuple_total += 1
                if confidence > t:
                    if new_tuple in X:
                        if confidence > X[new_tuple]:
                            X[(subj, obj)] = confidence
                            print("                Duplicate with higher confidence than existing record. Rewriting.")
                        else:
                            print(
                                "                Duplicate with lower confidence than existing record. Ignoring this.")
                    else:
                        X[(subj, obj)] = confidence
                        tuple_added += 1
                        print("                Adding to set of extracted relations")
                else:
                    print("                Confidence is lower than threshold confidence. Ignoring this.")
                print("                ==========")
    return X, tuple_added, tuple_total, annotated


def gpt_helper(X, tuple_added, tuple_total, sent, required_entities, r):
    extracted_entity_pairs = spacy_help_functions.create_entity_pairs(sent, required_entities)
    annotated = 0
    if len(extracted_entity_pairs) > 0:
        examples = []
        for ep in extracted_entity_pairs:
            entity1 = ep[1][1]
            entity2 = ep[2][1]
            if entity1 in required_entities[0] and entity2 in required_entities[1:]:
                examples.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})
            elif entity2 in required_entities[0] and entity1 in required_entities[1:]:
                examples.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})
        if len(examples) > 0:
            annotated = 1
            prompt_text = """ Given a sentence, extract all instances of the following relationship types as possible:
                relationship type: {}
                Output: [relationship: RELATIONSHIP; subject: {}; object: {}]

                An example for output is: {}
                Sentence: {} 
                Output: """.format(relations[r], ", ".join(required_entities[0]),
                                   " or ".join(required_entities[1:]), gpt_example[r], sent)

            model = 'text-davinci-003'
            max_tokens = 100
            temperature = 0.3
            top_p = 1
            frequency_penalty = 0
            presence_penalty = 0

            response = openai.Completion.create(
                model=model,
                prompt=prompt_text,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            response_text = response['choices'][0]['text']

            relationships = response_text.split("]")
            for relation in relationships:
                temp = relation.split('; ')

                if len(temp) < 3:  # no relation
                    continue
                subj = temp[1].split(': ')[1]
                subj = subj.strip()
                obj = temp[2].split(': ')[1]
                obj = obj.strip()

                print("                === Extracted Relation ===")
                print("                Sentence: {}".format(sent.text))
                print("                Subject: {} ; Object: {} ;".format(subj, obj))
                tuple_total += 1
                if (subj, obj) in X:
                    print("                Duplicate. Ignoring this.")
                else:
                    X[(subj, obj)] = 1
                    tuple_added += 1
                    print("                Adding to set of extracted relations")
                print("                ==========")

    return X, tuple_added, tuple_total, annotated


def main():
    # process the input
    method = sys.argv[1]
    google_api_key = sys.argv[2]
    google_engine_id = sys.argv[3]
    openai_key = sys.argv[4]
    r = sys.argv[5]
    t = float(sys.argv[6])
    q = sys.argv[7]
    k = int(sys.argv[8])

    print("Parameters:")
    print("Client key      =", google_api_key)
    print("Engine key      =", google_engine_id)
    print("OpenAI key      =", openai_key)
    print("Method  =", method[1:])
    print("Relation        =", relations[r])
    print("Threshold       =", t)
    print("Query           =", q)
    print("# of Tuples     =", k)
    print("Loading necessary libraries; This should take a minute or so ...)\n")

    # model
    spacy_model = spacy.load("en_core_web_lg")
    spanbert_model = None
    if method == "-spanbert":
        spanbert_model = SpanBERT("./pretrained_spanbert")
    openai.api_key = openai_key

    # iteration
    goal_check = False
    iter = -1
    visited_url = set()
    searched_q = set()
    searched_q.add(q.lower())
    X = {}
    while not goal_check:
        iter += 1
        print('=========== Iteration: {} - Query: {} ===========\n\n'.format(iter, q))
        retrieved = google_search(q, google_api_key, google_engine_id)['items']
        retrieved = retrieved[:min(10, len(retrieved))]
        cnt = 0
        for item in retrieved:
            cnt += 1
            # get the url
            url = item['link']
            print("URL ( {} / {}): {}".format(cnt, len(retrieved), url))
            if url in visited_url:
                print("        you should skip already-seen URLs")
                continue
            else:
                visited_url.add(url)
                print("        Fetching text from url ...")
                try:
                    webpage = requests.get(url)
                except:
                    print(
                        "        if you cannot retrieve the webpage (e.g., because of a timeout), just skip it and move on")
                    continue

            # get the text
            raw_text_str = BeautifulSoup(webpage.content, "html.parser").get_text()
            preprocessed_text = re.sub(u'\xa0', ' ', raw_text_str)
            preprocessed_text = re.sub('\t+', ' ', preprocessed_text)
            preprocessed_text = re.sub('\n+', ' ', preprocessed_text)
            preprocessed_text = re.sub(' +', ' ', preprocessed_text)
            preprocessed_text = preprocessed_text.replace('\u200b', '')

            if len(preprocessed_text) > 10000:
                print("        Trimming webpage content from {} to 10000 characters".format(len(preprocessed_text)))
                preprocessed_text = preprocessed_text[:10000]
            print("        Webpage length (num characters): {}".format(len(preprocessed_text)))
            print("        Annotating the webpage using spacy...")
            doc = spacy_model(preprocessed_text)
            sents = list(doc.sents)
            print(
                "        Extracted {} sentences. Processing each sentence one by one to check for presence of right pair of "
                "named entity types; if so, will run the second pipeline ...".format(len(sents)))

            # process sentences in webpage
            count = 0
            tuple_added = 0
            tuple_total = 0
            annotations = 0
            for sent in sents:
                count += 1
                if count % 5 == 0:
                    print("        Processed {} / {} sentences".format(count, len(sents)))
                if method == "-gpt3":
                    X, tuple_added, tuple_total, annotated = gpt_helper(X, tuple_added, tuple_total, sent,
                                                                        r2required_entities[r], r)
                elif method == "-spanbert":
                    X, tuple_added, tuple_total, annotated = spanbert_helper(X, tuple_added, tuple_total,
                                                                             spanbert_model, sent,
                                                                             r2required_entities[r], r, t)
                else:
                    raise NotImplementedError
                annotations += annotated
            print("        Extracted annotations for  {}  out of total  {}  sentences".format(annotations, len(sents)))
            print("        Relations extracted from this website: {} (Overall: {})".format(tuple_added, tuple_total))

        # check the goal
        if len(X) >= k:
            goal_check = True
        else:
            # sort X
            sorted_items = sorted(X.items(), key=lambda x: x[1], reverse=True)
            X = {}
            for k, v in sorted_items:
                X[k] = v
            # add the highest unseen query
            for k, v in sorted_items:
                if " ".join(k).lower() in searched_q:
                    continue
                q = " ".join(k).lower()
                searched_q.add(q)
                break

    print("================== ALL RELATIONS for per:{} ( {} ) =================".format(relations[r].lower(), len(X)))
    if method == "-gpt3":
        for subject, object in X.keys():
            print("Subject: {}                | Object: {}".format(subject, object))
    elif method == "-spanbert":
        sorted_items = sorted(X.items(), key=lambda x: x[1], reverse=True)
        for k, v in sorted_items:
            subject, object = k
            print("Confidence: {}           | Subject: {}           | Object: {}".format(X[(subject, object)], subject,
                                                                                         object))
    print("Total # of iterations =", iter + 1)


if __name__ == "__main__":
    main()