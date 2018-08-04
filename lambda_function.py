"""
-*- coding: utf-8 -*-
========================
Bot
========================

Contributor: Chirag Rathod (Srce Cde)

========================
"""

import sys, os, boto3, urllib, io
import config
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/lib")
import pandas as pd

client = boto3.client('lex-models')
lam = boto3.client('lambda')
s3 = boto3.client("s3")

def create_bot(intent_list = None, slot_list = None, arn = None):
    temp = []
    for i in intent_list:
        for j, k in i.items(): 
            temp.append({"intentName": str(j), "intentVersion": str("$LATEST")})

    for i in intent_list:
        for j, k in i.items():
                response = client.put_intent(
                    name=str(j),
                    # description="description",
                    slots=slot_list,
                    sampleUtterances=[k],
                    fulfillmentActivity={ 
                    "type": "CodeHook",
                    "codeHook": { 
                       "messageVersion": "1.0",
                       "uri": str(arn)
                    },
                    }
                    # checksum=checksum
                )
    response = client.put_bot(name="playbot",
            description="cricket",
            intents = temp,
            clarificationPrompt = {"messages": [
            {
                "contentType": "PlainText",
                "content": "Sorry, can you please repeat that?",
                "groupNumber": 1
            }
        ],
        "maxAttempts": 5},
        abortStatement = {
        "messages": [
            {
                "contentType": "PlainText",
                "content": "Sorry, i could not understand. Goodbye.",
                "groupNumber": 1
            }
        ]
    },
    idleSessionTTLInSeconds= 300,
    locale = "en-US",
    # checksum = "$LATEST",    
    processBehavior= "BUILD",
    childDirected= True)
    # createVersion= False)

    # for i in slot_list:

    #         response = client1.put_slot_type(
    #                 name="auto_"+str(i),
    #                 # description='string',
    #                 # enumerationValues=[
    #                 #     {
    #                 #         'value': 'string',
    #                 #         'synonyms': [
    #                 #             'string',
    #                 #         ]
    #                 #     },
    #                 # ],
    #                 # checksum='string',
    #                 # valueSelectionStrategy='ORIGINAL_VALUE'|'TOP_RESOLUTION',
    #                 # createVersion=True|False
    #             )


def lambda_handler(event, context):
    if event:
        file_obj = event['Records'][0]
        filename = urllib.parse.unquote_plus(str(file_obj['s3']['object']['key']))
        fileObj = s3.get_object(Bucket = config.trigger_bucket, Key = filename)
        csv_path = io.BytesIO(fileObj["Body"].read())
        df = pd.read_csv(csv_path, sep='\t')
        df.drop(df.columns[-5:], axis = 1, inplace=True)
        d = dict(df.dtypes)
        sl = {}
        temp = []
        il = []

        for i,j in d.items():
            if j in ["int64", "float64"]:
                temp.append({"slotType": "AMAZON.NUMBER", "name": i.lower().strip().replace(" ", "_"), "slotConstraint": "Optional"})
            if i == "Player":
                temp.append({"slotType": "AMAZON.Person", "name": i.lower().strip().replace(" ", "_"), "slotConstraint": "Optional"})
            if i == "Span":
                temp.append({"slotType": "AMAZON.DATE", "name": i.lower().strip().replace(" ", "_"), "slotConstraint": "Optional"})

        intent_utter = config.intent_utterence
        intent_utter_split = intent_utter.split(",")
        for i in intent_utter_split:
            temp_split = i.split(":")
            il.append({temp_split[0]: temp_split[1]})

        # il = [{"maxRuns": "what is the high score of {player}"}, {"scoreXcentury": "who scored more than {century} century"}, {"run": "how many runs did {player} scored"}]

        resp = lam.create_function(FunctionName = config.lex_func_name, Runtime = "python3.6", Role = config.role, Handler = "lambda_function.lambda_handler", Code = {"S3Bucket": config.bucket_name, "S3Key": config.bucket_key}, Timeout= 300)
        arn = resp["FunctionArn"]
        lam.add_permission(FunctionName = arn, StatementId = "unique", Action = "lambda:invokeFunction", Principal = "lex.amazonaws.com")

        create_bot(intent_list = il, slot_list = temp, arn = arn)
