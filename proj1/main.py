#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author_1__ = "Yipeng Geng, yg2913"
__author_2__ = "Yufei Liu, yl5099"

import pprint
import sys
from googleapiclient.discovery import build
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

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

def UI(query, google_api_key, google_engine_id, precision, first_iter=False):
    relevant_d = []
    non_relevant_d = []
    print("Parameters:")
    print("Client key  =", google_api_key)
    print("Engine key  =", google_engine_id)
    print("Query       =", query)
    print("Precision   =", precision)
    print("Google Search Results:")
    print("======================")
    retrieved = google_search(query, google_api_key, google_engine_id)['items']

    # If in the first iteration there are fewer than 10 results overall, then the program simply terminate
    if first_iter and len(retrieved) < 10:
        return True, [], []
    # pprint.pprint(retrieved)
    correct = 0.0
    for i, itm in enumerate(retrieved):
        print("Result", i+1)
        print('[')
        print(' URL: ', itm['formattedUrl'])
        print(' Title: ', itm['title'])
        print(' Summary', itm['snippet'])
        print(']')
        print()
        yn = input('Relevant (Y/N)?')
        if yn.lower() in {'y', 'yes'}:
            correct += 1
            relevant_d.append(itm['title'].lower()+itm['snippet'].lower())
        else:
            non_relevant_d.append(itm['title'].lower()+itm['snippet'].lower())

    # If in the first iteration there are no relevant results among the top-10 pages that Google returns,
    # then the program simply terminate
    if first_iter and correct == 0.0:
        return True, [], []

    print("======================")
    print("FEEDBACK SUMMARY")
    print("Query", query)
    print("Precision", correct / 10)
    if correct/10 < precision:
        print("Still below the desired precision of 0.9")
        return False, relevant_d, non_relevant_d
    else:
        print("Desired precision reached, done")
        return True, [], []

def Rocchio(q_vectors, relevant_vectors, non_relevant_vectors, query, words):
    print("Indexing results ....")
    print("Indexing results ....")
    alpha = 1.0
    beta = 1.0
    gamma = 1.0

    new_q = alpha * q_vectors + beta * np.sum(relevant_vectors, axis=0) / len(relevant_vectors) \
                       - gamma * np.sum(non_relevant_vectors, axis=0) / len(non_relevant_vectors)

    new_q = new_q[0]
    for i in range(len(new_q)):
        if new_q[i] < 0:
            new_q[i] = 0
    res = list(zip(new_q, words))
    res.sort(key=lambda x: x[0], reverse=True)
    # print(res)
    q_words = query.split(" ")
    cnt = 0
    n_words = []
    for pair in res:
        w = pair[1]
        if w not in q_words:
            q_words.append(w)
            n_words.append(w)
            cnt += 1
        if cnt == 2:
            break
    # print(np.array(new_query_vector).shape)
    print("Augmenting by ", " ".join(n_words))
    return " ".join(q_words)

def main():

    google_api_key = sys.argv[1]
    google_engine_id = sys.argv[2]
    precision = float(sys.argv[3])
    query = sys.argv[4].lower()
    goal_check = False
    first_iter = True

    while not goal_check:
        goal_check, relevant_d, non_relevant_d = UI(query, google_api_key, google_engine_id, precision, first_iter)
        if goal_check:
            break
        first_iter = False

        corpus = [query] + relevant_d + non_relevant_d
        # print(len(corpus))
        transfer = TfidfVectorizer(stop_words=['a', 'the'])
        vectors = transfer.fit_transform(corpus).toarray()
        # print(vectors)
        # print(len(vectors))
        # print(np.array(vectors.shape))
        q_vectors, relevant_vectors, non_relevant_vectors = vectors[:1,:], vectors[1:1+len(relevant_d),:], vectors[1+len(relevant_d):,:]
        words = transfer.get_feature_names()
        # print(np.array(q_vectors).shape)    # (1,V)
        # print(np.array(relevant_vectors).shape)  # (6, V)
        # print(np.array(non_relevant_vectors).shape)  # (4, V)

        query = Rocchio(q_vectors, relevant_vectors, non_relevant_vectors, query, words)

        #print(X)
        #print()
        #print([query]+relevant_d+non_relevant_d)



if __name__ == "__main__":
    main()
