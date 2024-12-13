#!/usr/bin/env python3

import json
import time
from flask import Flask, request, jsonify
from main import main
from replace_main import change_main

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the plagiarism detector\n"

@app.route("/check")
def check_plagiarism():
    try:
        start_time = time.time()
        data = main()
        end_time = round((time.time() - start_time), 3)
        print(f'execution time: {end_time}ms')
        similar_docs = json.loads(data)
        
        return jsonify({
    'similar_docs': similar_docs,
    'execution_time': end_time
    }), 200
    
    except Exception as e:
        return jsonify({
    'status': 'error',
    'message': str(e)
    }), 500
    
@app.route("/replace", methods=["POST"])
def replace_document():
    try:
        content = request.json.get('text', '') 
        
        print(content)
        
        change_main(content)
        
        return check_plagiarism()
    
    except Exception as e:
        return jsonify({
    'status': 'error',
    'message': str(e)
    }), 500
    
if __name__ == "__main__":
    app.run(debug=True)