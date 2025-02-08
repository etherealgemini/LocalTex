def cer(r: list, h: list) -> float:
    """
    Calculation of CER with Levenshtein distance.
    """
    # initialisation
    import numpy
    d = numpy.zeros((len(r) + 1) * (len(h) + 1), dtype=numpy.uint16)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    return d[len(r)][len(h)] / float(len(r))

def cer_avg(r:list, h:list, sep=None) -> float:
    tot_cer = 0
    assert len(r)==len(h)
    n = len(r)
    for i in range(n):
        r_ = r[i]
        h_ = h[i]
        if isinstance(r_, str):
            if sep is None:
                r_ = [x for x in r_]
            else:
                r_ = r_.split(sep=sep)
        if isinstance(h_, str):
            if sep is None:
                h_ = [x for x in h_]
            else:
                h_ = h_.split(sep=sep)

        tot_cer += cer(r_,h_)

    return tot_cer/n


import fastwer
import re
from unidecode import unidecode


def normalize_text(text, is_case_sensitive=False, include_special_chars=False, transliterate_ascii=True):
    """
    Normalize a given text string by applying various transformations.

    Parameters:
    - text (str): The text to be normalized.
    - is_case_sensitive (bool): If False, converts text to lowercase.
    - include_special_chars (bool): If False, removes all non-alphanumeric characters.
    - transliterate_ascii (bool): If True, transliterates text to ASCII.

    Returns:
    - str: The normalized text string.
    """
    # Remove extra spaces and strip leading/trailing spaces
    text = re.sub(' +', ' ', text).strip()

    # Convert text to lowercase if not case-sensitive
    if not is_case_sensitive:
        text = text.lower()

    # Remove special characters
    if not include_special_chars:
        text = ''.join(char for char in text if char.isalnum() or char.isspace())

    # Transliterate to ASCII
    if transliterate_ascii:
        text = unidecode(text)

    return text


def calculateCERMatch(text_pred, text_gt, cer_threshold=50.0, composite_weights=(0.5, 0.2, 0.15, 0.15),
                      is_case_sensitive=False, include_special_chars=False, transliterate_ascii=True,
                      return_word_lists=False, normalized=False):
    """
    Calculate the CER match score between predicted text and ground truth text.

    Parameters:
    - text_pred (str): Predicted text.
    - text_gt (str): Ground truth text.
    - cer_threshold (float): CER threshold for considering a match.
    - composite_weights (tuple): Weights for matched, errors, invented, missed words.
    - is_case_sensitive (bool): Case sensitivity flag for normalization.
    - include_special_chars (bool): Flag to include special characters in normalization.
    - transliterate_ascii (bool): Flag to transliterate text to ASCII in normalization.
    - return_word_lists (bool): Flag to return lists of word categories.

    Returns:
    - dict: Scores including composite score and ratios of match categories.
    - dict (optional): Lists of words in each match category.
    """
    # Normalize texts
    text_pred_norm = normalize_text(text_pred, is_case_sensitive, include_special_chars, transliterate_ascii)
    text_gt_norm = normalize_text(text_gt, is_case_sensitive, include_special_chars, transliterate_ascii)

    # Split normalized texts into words
    words_pred = text_pred_norm.split(" ")
    words_gt = text_gt_norm.split(" ")
    total_words = len(words_gt)

    matched, errors, invented, missed = [], [], [], []

    for word_pred in words_pred:
        if word_pred in words_gt:
            matched.append(word_pred)
            words_gt.remove(word_pred)
        else:
            cer_values = [(gt_word, fastwer.score_sent(word_pred, gt_word, char_level=True)) for gt_word in words_gt]
            min_cer_word, min_cer_value = min(cer_values, key=lambda x: x[1])
            if min_cer_value <= cer_threshold:
                errors.append((word_pred, min_cer_word, min_cer_value / 100.))
                words_gt.remove(min_cer_word)
            else:
                invented.append(word_pred)

    missed.extend(words_gt)

    # Calculate percentages
    matched_pct = len(matched) / total_words
    errors_pct = len(errors) / total_words
    invented_pct = len(invented) / total_words
    missed_pct = len(missed) / total_words

    # Apply weights to calculate composite score
    weight_matched, weight_errors, weight_invented, weight_missed = composite_weights
    composite_score = (matched_pct * weight_matched +
                       (1 - sum(e[2] for e in errors) / len(errors) if errors else 1) * weight_errors +
                       (1 - invented_pct) * weight_invented +
                       (1 - missed_pct) * weight_missed) / sum(composite_weights)

    scores = {
        "composite_score": composite_score,
        "ratio_matched": matched_pct,
        "ratio_errors": errors_pct,
        "ratio_invented": invented_pct,
        "ratio_missed": missed_pct
    }

    if return_word_lists:
        return scores, {
            "matched": matched,
            "errors": errors,
            "invented": invented,
            "missed": missed
        }
    return scores
