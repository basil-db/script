# this file includes functions that take papers as inputs and returns some filtered out information from the paper

import rrnlp
from robotreviewer.robots import bias_robot
import spacy
from nltk import sent_tokenize
import re

trial_reader = rrnlp.TrialReader()


def robotreview(paper_infos, with_ext_bias=False):
    #paper infos: [[title,abstract,...],...,[title,abstract,...]]
    reviews = []
    if with_ext_bias==True:
        b = bias_robot.BiasRobot()
        nlp = spacy.load("en_core_web_sm")
    ti_abs = {"ti": paper_infos[0], "ab": paper_infos[1]}
    try:
        preds = trial_reader.read_trial(ti_abs, process_rcts_only=False)
    except:
        return None
    is_rct = preds.get('rct_bot').get('is_rct')
    bias_ab = preds.get('bias_ab_bot').get('prob_low_rob')
    effect = preds.get('punchline_bot').get('effect')
    punchline_text = preds.get('punchline_bot').get('punchline_text')
    num_randomized = preds.get('sample_size_bot').get('num_randomized')
    outcomes = preds.get('pico_span_bot').get('o')
    interventions = preds.get('pico_span_bot').get('i_mesh')
    population = preds.get('pico_span_bot').get('p')
    outcome_meshs = preds.get('pico_span_bot').get('o_mesh')
    population_meshs = preds.get('pico_span_bot').get('p_mesh')
    if with_ext_bias==True:
        doc = nlp(paper_infos[2])
        data = {'parsed_text': doc, 'text': paper_infos[2]}
        biases = b.pdf_annotate(data)

    reviews.append({'effect': effect, 'punchline_text': punchline_text, 'outcomes': outcomes, 'outcome_meshs': outcome_meshs, 'population': population, 'population_meshs': population_meshs, 'intervention_meshs': interventions, 'num_randomized': num_randomized, 'is_rct': is_rct, 'bias_ab': bias_ab})#, 'biases': biases})
    return reviews

def extract_HR(text):
    # get the Hazard Ratio from text by rule-based matching

    if "Results: " in text:
        text = text.split("Results: ", 1)[1]

    sentences = sent_tokenize(text)
    for sentence in sentences:

        sentence = re.sub('\s', ' ', sentence)  # sometimes space chars give problems
        sentence = re.sub('·', '.', sentence)

        hazard_match = re.findall("(\[HR|\(HR|[Hh]azard ratio|[Hh]azard ratio \[HR\]|[Hh]azard ratio \(HR\))[,:= ]+(\d+\.?\d*)", sentence)
        if hazard_match != []:
            hazard_match2 = re.findall("(HR|[Hh]azard ratio|[Hh]azard ratio \[HR\]|[Hh]azard ratio \(HR\))[,:= ]+(\d+\.?\d*).+?(\d+\.?\d*(-| to )\d+\.?\d*).*?[\)\]]", sentence)
            if hazard_match2 != []:
                if '-' in hazard_match2[0][2]:
                    cisplit = hazard_match2[0][2].split('-')
                else:
                    cisplit = hazard_match2[0][2].split(' to ')
                if float(hazard_match[0][1]) > float(cisplit[0]) and float(hazard_match[0][1]) < float(cisplit[1]):

                    return (float(hazard_match[0][1]), float(cisplit[0]), float(cisplit[1]))

            return (float(hazard_match[0][1]), float(hazard_match[0][1]), float(hazard_match[0][1]))

    return None

def extract_PFS(text, pki=None):
    # get the median progression free survival from text by rule-based matching

    if "Results: " in text:
        text = text.split("Results: ", 1)[1]
    sentences = sent_tokenize(text)
    for sentence in sentences:

        sentence = re.sub('\s', ' ', sentence) #sometimes space chars give problems
        sentence = re.sub('·', '.', sentence)
        sentence = re.sub(', ', ' ', sentence)

        PFS_match = re.findall("([Mm]edian|[Mm]ean).+?(PFS|[Pp]rogression[- ]free survival) .+? (\d+\.?\d*) (days|weeks|months|mo |years)", sentence) #Mean actually doensn't appear, just as test

        if PFS_match != []:

            PFS_match_2 = re.findall("([Mm]edian|[Mm]ean) (PFS|[Pp]rogression[- ]free survival) .+? (\d+\.?\d*) (days|weeks|months|mo |years).+?( for | in )(.+?group |.+?therapy )?(and|vs|versus|compared to|as compared with) (\d+\.?\d*) (weeks|months|mo |years).+?( for | in )(.+?group|.+?therapy)?", sentence)

            if PFS_match_2 != []:

                CI = re.findall("(\d+\.?\d*) (days|weeks|months|mo |years) [\(\[].*?(\d+\.?\d*-\d+\.?\d*)", sentence)

                pki = pki[0].lower()
                if pki in PFS_match_2[0][5]:
                    PFS = PFS_match_2[0][0:4]
                elif pki in PFS_match_2[0][-1]:
                    PFS = PFS_match_2[0][0:2] + PFS_match_2[0][7:-2]
                elif 'placebo' in PFS_match_2[0][-1]:
                    PFS = PFS_match_2[0][0:4]
                elif 'placebo' in PFS_match_2[0][5]:
                    PFS = PFS_match_2[0][0:2] + PFS_match_2[0][7:-2]
                else:
                    PFS = PFS_match_2[0][0:4]

                PFS_CI = ''
                for c in CI:
                    if c[0] == PFS[2]:
                        PFS_CI = c[2]

                return PFS[2:5] + (PFS_CI,)

            PFS_match_3 = re.findall("([Mm]edian|[Mm]ean).+?(PFS|[Pp]rogression[- ]free survival) .+? (\d+\.?\d*) (and|vs|versus|compared to|as compared with) (\d+\.?\d*) (days|weeks|months|mo |years)", sentence)

            if PFS_match_3 != []:
                CI = re.findall("(\d+\.?\d*) (days|weeks|months|mo |years) [\(\[].*?(\d+\.?\d*-\d+\.?\d*)", sentence)
                if CI != []:
                    CI = CI[0][2]
                else:
                    CI = ''
                #print((PFS_match_3[0][2], PFS_match_3[0][-1], CI), sentence)
                return (PFS_match_3[0][2], PFS_match_3[0][-1], CI)

            CI = re.findall("(PFS|[Pp]rogression[- ]free survival) .+? (\d+\.?\d*) (days|weeks|months|mo |years).*?[\(\[].+?(\d+\.?\d*?-\d+\.?\d*)", sentence)
            if CI != []:
                PFS_CI = CI[0][-1]
            else:
                PFS_CI = ''

            return PFS_match[0][2:5] + (PFS_CI, )

        else:
            PFS_match = re.findall("([Mm]edian|[Mm]ean) (PFS|[Pp]rogression[- ]free survival)[:= ](\d+\.?\d*) (days|weeks|months|mo |years)", sentence)
            if PFS_match != []:

                return PFS_match[0][2:4] + (' ',)

    return None



def extract_OS(text, pki=None):
    # get the median overall survival from text by rule-based matching

    if "Results: " in text:
        text = text.split("Results: ", 1)[1]
    sentences = sent_tokenize(text)
    for sentence in sentences:

        sentence = re.sub('\s', ' ', sentence) #sometimes space chars give problems
        sentence = re.sub('·', '.', sentence)
        sentence = re.sub(', ', ' ', sentence)

        PFS_match = re.findall("([Mm]edian|[Mm]ean).+?(OS|[Oo]verall [Ss]urvival).+?(\d+\.?\d*) (days|weeks|months|mo |years)", sentence) #Mean actually doensn't appear, just as test
        if PFS_match != []:
            PFS_match_2 = re.findall("([Mm]edian|[Mm]ean).+?(OS|[Oo]verall [Ss]urvival) .+? (\d+\.?\d*) (days|weeks|months|mo |years).+?( for | in )(.+?group |.+?therapy )?(and|vs|versus|compared to|as compared with) (\d+\.?\d*) (days|weeks|months|mo |years).+?( for | in )(.+?group|.+?therapy)?", sentence)

            if PFS_match_2 != []:

                CI = re.findall("(\d+\.?\d*) (days|weeks|months|mo |years) [\(\[].*?(\d+\.?\d*-\d+\.?\d*)", sentence)

                pki = pki[0].lower()
                if pki in PFS_match_2[0][5]:
                    PFS = PFS_match_2[0][0:4]
                elif pki in PFS_match_2[0][-1]:
                    PFS = PFS_match_2[0][0:2] + PFS_match_2[0][7:-2]
                elif 'placebo' in PFS_match_2[0][-1]:
                    PFS = PFS_match_2[0][0:4]
                elif 'placebo' in PFS_match_2[0][5]:
                    PFS = PFS_match_2[0][0:2] + PFS_match_2[0][7:-2]
                else:
                    PFS = PFS_match_2[0][0:4]

                PFS_CI = ''
                for c in CI:
                    if c[0] == PFS[2]:
                        PFS_CI = c[2]

                return PFS[2:5] + (PFS_CI,)

            PFS_match_3 = re.findall("([Mm]edian|[Mm]ean).+?(OS|[Oo]verall [Ss]urvival) .+? (\d+\.?\d*) (and|vs|versus|compared to|as compared with) (\d+\.?\d*) (days|weeks|months|mo |years)", sentence)

            if PFS_match_3 != []:
                CI = re.findall("(\d+\.?\d*) (weeks|months|mo |years) [\(\[].*?(\d+\.?\d*-\d+\.?\d*)", sentence)
                if CI != []:
                    CI = CI[0][-1]
                else:
                    CI = ''

                return (PFS_match_3[0][2], PFS_match_3[0][-1], CI)

            CI = re.findall("([Mm]edian|[Mm]ean).+?(OS|[Oo]verall [Ss]urvival) .+? (\d+\.?\d*) (days|weeks|months|mo |years).*?[\(\[].+?(\d+\.?\d*?-\d+\.?\d*)", sentence)
            if CI != []:
                PFS_CI = CI[0][-1]
            else:
                PFS_CI = ''

            return PFS_match[0][2:5] + (PFS_CI, )

        else:
            PFS_match = re.findall("([Mm]edian|[Mm]ean).+?(OS|[Oo]verall [Ss]urvival)[:= ](\d+\.?\d*) (days|weeks|months|mo |years)", sentence)
            if PFS_match != []:

                return PFS_match[0][2:4] + (' ',)

    return None
