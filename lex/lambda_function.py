"""
-*- coding: utf-8 -*-
========================
Bot
========================

Contributor: Chirag Rathod (Srce Cde)

========================
"""

import sys, os, boto3
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/lib")
import pandas as pd

def confirm_intent(session_attributes, intent_name, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        }
    }

def lambda_handler(event, context):
    intent_name =   event['currentIntent']['name']
    session_attributes = event['sessionAttributes']
    df = pd.read_csv("data.csv", sep="\t")
    df.drop(df.columns[-5:], axis = 1, inplace=True)
    df.columns = ["Player", "Span", "Match", "Runs", "High Score", "Average", "Century", "Wickets"]
    df['Player'] = df['Player'].map(lambda x: x.strip())
    slots = event['currentIntent']['slots']

    if intent_name == "maxRuns":
        d = df.loc[df["Player"] == slots["player"]]
        msg = "The High Score of {} is {}".format(slots["player"], d["High Score"].values[0])
        return confirm_intent(session_attributes, intent_name, msg)
    if intent_name == "runs":
        d = df.loc[df["Player"] == slots["player"]]
        msg = "{} scored {}".format(slots["player"], d["Runs"].values[0])
        return confirm_intent(session_attributes, intent_name, msg)
    if intent_name == "scoreXcentury":
        d = df.loc[df["Century"] > int(slots["century"])]
        if not d.empty:
            p = ', '.join(i for i in d["Player"])
            msg = "{} score more than {} century".format(p, slots["century"])
            return confirm_intent(session_attributes, intent_name, msg)
        else:
            msg = "No records found"
            return confirm_intent(session_attributes, intent_name, msg)
