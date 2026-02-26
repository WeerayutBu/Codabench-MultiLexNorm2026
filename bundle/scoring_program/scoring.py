import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

def evaluate(raw, gold, pred, ignCaps=False, verbose=False, info=False):
    cor = 0
    changed = 0
    total = 0

    if len(gold) != len(pred):
        err('Error: gold normalization contains a different numer of sentences(' + str(len(gold)) + ') compared to system output(' + str(len(pred)) + ')')

    for sentRaw, sentGold, sentPred in zip(raw, gold, pred):
        if len(sentGold) != len(sentPred):
            err('Error: a sentence has a different length in you output, check the order of the sentences')
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

if __name__ == "__main__":

    reference_dir  = os.path.join('/app/input/', 'ref') # dev/test label will move to here.
    prediction_dir = os.path.join('/app/input/', 'res') # submission data will be here.
    save_path      = os.path.join('/app/output/', 'scores.json') # show in readerboard.

    print('Read label and prediction')
    label = pd.read_json(os.path.join(reference_dir, 'label.json'))
    pred = pd.read_json(os.path.join(prediction_dir, 'predictions.json'))
    
    assert label['raw'].tolist() == pred['raw'].tolist()

    ########################
    # Calculate score here
    ########################
    scores = {}
    for lang in label['lang'].unique():
        ## Filter data
        label_lang = label[label["lang"] == lang]
        pred_lang = pred[pred["lang"] == lang]
        assert label_lang["raw"].tolist() == pred_lang["raw"].tolist()
        ## Evaluate
        lai, accuracy, err = evaluate(
            raw  = label_lang['raw'].tolist(), 
            gold = label_lang['norm'].tolist(), 
            pred = pred_lang['pred'].tolist()
        )

        err *= 100
        scores[f"{lang}"] = err
        print(f"{lang}: {err}")

    # Average and weighted average scores
    langs = ["th", "ja", "ko", "id", "vi"]
    err_average = np.mean(list(scores.values()))

    new_langs = [k for k in scores if k in langs]
    orig_langs = [k for k in scores if k not in langs]
    err_new = np.mean([scores[k] for k in new_langs])
    err_orig = np.mean([scores[k] for k in orig_langs])
    err_weighted = 0.5 * err_new + 0.5 * err_orig
    # Update scores
    scores['err-average'] = err_average
    scores['err-weighted'] = err_weighted
    scores['err-new'] = err_new
    scores['err-orig'] = err_orig
    
    # Info
    print(f"err-average: {err_average}")
    print(f"err-weighted: {err_weighted}")
    print(f"err-new: {err_new}")
    print(f"err-orig: {err_orig}")

    with open(save_path, 'w') as score_file:
        score_file.write(json.dumps(scores))
