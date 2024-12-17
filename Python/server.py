#!/usr/bin/env python3

import json
import time
from flask import Flask, request, jsonify
from main import main
from replace_main import change_main
from serve_file import read_content

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
    
@app.route("/read", methods=["GET"])
def read_file():
    try:
        # Fetch 'name' parameter from the query string
        file_name = request.args.get('name', '')
        print(f"Requested file: {file_name}")
        
        # Check if file name is provided
        if not file_name:
            return jsonify({
                'status': 'error',
                'message': "Missing 'name' parameter in query"
            }), 400
        
        # Read the file content
        file_content = read_content(file_name)
        
        # Return success response
        return jsonify({
            'status': 'success',
            'file_content': file_content
        })
    
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': f"File '{file_name}' not found"
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
    
if __name__ == "__main__":
    app.run(debug=True)