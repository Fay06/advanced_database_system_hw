# Yipeng Geng yg2913
# Yufei Liu
import csv
import sys
from functools import reduce
from collections import defaultdict

def get_data(dir):
    data = []
    with open(dir) as f:
        reader = csv.reader(f)
        for r in reader:
            s = set()
            for i in r:
                s.add(i)
            data.append(s)
    return data

def first(data, min_sup):
    item_cnt = defaultdict(int)
    for basket in data:
        for item in basket:
            item_cnt[item] += 1

def get_sets(all_items, last_sets):
    if len(last_sets)==0:
        return [set([i]) for i in all_items]
    new_sets = []
    for s1 in last_sets:
        for s2 in last_sets:
            new_set = s1.union(s2)
            if len(new_set) == len(s1)+1:
                if frozenset(new_set) not in new_sets:
                    new_sets.append(frozenset(new_set))
    return new_sets

def get_supports(data, sets):
    supports_dic = defaultdict(float)
    for basket in data:
        for s in sets:
            if s.issubset(basket):
                supports_dic[frozenset(s)] += 1
    for key in supports_dic:
        supports_dic[key] /= len(data)
    return supports_dic


def get_frequent_itemsets(data, min_sup):
    # get frequent itemsets
    all_sets = []
    all_supports = defaultdict(float)
    all_items = reduce(lambda x, y: x.union(y), data)
    cand_sets = get_sets(all_items, [])
    supports = get_supports(data, cand_sets)
    last_sets = [frozenset(s) for s in cand_sets if supports[frozenset(s)] >= min_sup]
    all_sets += last_sets[:]
    all_supports.update(supports)
    while last_sets:
        cand_sets = get_sets(all_items, last_sets)
        supports = get_supports(data, cand_sets)
        last_sets = [frozenset(s) for s in cand_sets if supports[frozenset(s)] >= min_sup]
        all_sets += last_sets[:]
        all_supports.update(supports)
    print('==Frequent itemsets (min_sup={}%)'.format(min_sup*100))
    all_sets.sort(key=lambda x: all_supports[x], reverse=True)
    for s in all_sets:
        print('{}, {}%'.format(list(s), round(all_supports[s]*100, 2)))
    print()
    return all_sets, all_supports

def get_rules(all_sets, all_supports, min_conf):
    # get rules from frequent itemsets
    rules = []
    for s in all_sets:
        if len(s)==1:
            continue
        for item in s:
            RHS = item
            LHS = s.difference({item})
            supp = all_supports[s]
            conf = supp/all_supports[LHS]
            if conf >= min_conf:
                rules.append((tuple(LHS), RHS, conf, supp))
    print('==High-confidence association rules (min_conf={}%)'.format(min_conf*100))
    rules.sort(key=lambda x: (x[2], x[3]), reverse=True)
    for r in rules:
        print('{} => {} (Conf: {}%, Supp: {}%)'.format(list(r[0]), [r[1]], round(r[2]*100, 2), round(r[3]*100, 2)))
    print()
    return rules

if __name__ == '__main__':
    path = sys.argv[1]
    min_sup = float(sys.argv[2])
    min_conf = float(sys.argv[3])
    data = get_data(path)
    all_sets, all_supports = get_frequent_itemsets(data, min_sup)
    rules = get_rules(all_sets, all_supports, min_conf)

