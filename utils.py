import json
from collections import defaultdict

def err(msg):
    print('Error: ' + msg)
    exit(0)
    
def loadNormData(path):
    rawData = []
    goldData = []
    curSent = []

    for line in open(path):
        tok = line.strip().split('\t')

        if tok == [''] or tok == []:
            rawData.append([x[0] for x in curSent])
            goldData.append([x[1] for x in curSent])
            curSent = []

        else:
            if len(tok) > 2:
                err('erroneous input, line:\n' + line + '\n in file ' + path + ' contains more then two elements')
            if len(tok) == 1:
                tok.append('')
            curSent.append(tok)

    # in case file does not end with newline
    if curSent != []:
        rawData.append([x[0] for x in curSent])
        goldData.append([x[1] for x in curSent])
    return rawData, goldData


def save_data(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)



def sampling_dev(ds, ratio=0.5):
    # group indices by language
    lang_to_indices = defaultdict(list)
    for i, lang in enumerate(ds["lang"]):
        lang_to_indices[lang].append(i)

    selected_indices = []
    for lang, indices in lang_to_indices.items():
        k = max(1, int(len(indices) * ratio))  
        selected_indices.extend(indices[:k])   # deterministic slice

    return ds.select(sorted(selected_indices))


def counting(data):
    counts = {}
    for item in data:
        sentRaw = item['raw']
        sentGold = item['norm']
        for wordRaw, wordGold in zip(sentRaw, sentGold):
            if wordRaw not in counts:
                counts[wordRaw] = {}
            if wordGold not in counts[wordRaw]:
                counts[wordRaw][wordGold] = 0
            counts[wordRaw][wordGold] += 1
    return counts

def mfr(input_sent, counts):
    predictions = []
    for word in input_sent:
        if word in counts:
            replacement = max(counts[word], key=counts[word].get)
        else:
            replacement = word
        predictions.append(replacement)
    return predictions



def evaluate(raw, gold, pred, ignCaps=False, verbose=False, info=True):
    cor = 0
    changed = 0
    total = 0

    if len(gold) != len(pred):
        print('Error: gold normalization contains a different numer of sentences(' + str(len(gold)) + ') compared to system output(' + str(len(pred)) + ')')

    for sentRaw, sentGold, sentPred in zip(raw, gold, pred):
        if len(sentGold) != len(sentPred):
            print('Error: a sentence has a different length in you output, check the order of the sentences')
        for wordRaw, wordGold, wordPred in zip(sentRaw, sentGold, sentPred):
            if ignCaps:
                wordRaw = wordRaw.lower()
                wordGold = wordGold.lower()
                wordPred = wordPred.lower()
            if wordRaw != wordGold:
                changed += 1
            if wordGold == wordPred:
                cor += 1
            elif verbose:
                print(wordRaw, wordGold, wordPred)
            total += 1

    accuracy = cor / total
    lai = (total - changed) / total
    err = (accuracy - lai) / (1-lai)

    if info:
        print('Baseline acc.(LAI): {:.2f}'.format(lai * 100)) 
        print('Accuracy:           {:.2f}'.format(accuracy * 100)) 
        print('ERR:                {:.2f}'.format(err * 100))

    return lai, accuracy, err
