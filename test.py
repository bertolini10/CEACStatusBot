import os
import argparse


from CEACStatusBot import query_status,OnnxCaptchaHandle

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("LOCATION", type=str, help="A string parameter")
    parser.add_argument("NUMBER", type=str, help="A string parameter")
    args = parser.parse_args()
    #LOCATION = 'RDJ'
    #NUMBER = '2023524032'
    print(query_status(args.LOCATION,args.NUMBER,OnnxCaptchaHandle("captcha.onnx")))
except KeyError:
    print("ENV Error")
