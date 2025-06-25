from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
import serial # type: ignore
from utils.records_management import set_username, set_value, get_clothing_items
import threading
import time
from multiprocessing import Process
import washingmachine as washingmachine  # This is your washingmachine.py file

app = Flask(__name__)

# First page the user lands on where they can enter their username
@app.route('/')
def index():
    return render_template('index.html')

# Submit username and redirect to slider page
@app.route('/submit_username', methods=['POST'])
def submit_username():
    username, user_id = set_username(request.form.get('username'))
    if username:
        return redirect(url_for('slider', user_id=user_id))
    else:
        return redirect(url_for('index'))
  
# Slider page where the user can predict their score
@app.route('/slider/<user_id>')
def slider(user_id):
    return render_template('slider.html', user_id=user_id)

# Submit the prediction and redirect to the scan page
@app.route('/slider/<user_id>/submit', methods=['POST'])
def submit_score(user_id):
    # Get the score from the request
    score = request.form.get('score')
    # Save the score to the database
    set_value(user_id, score, "predicted_score")
    return redirect(url_for('scan', user_id=user_id))

# Page where the user can scan their clothing
@app.route('/scan/<user_id>')
def scan(user_id):
    # Get the clothing items from the database
    clothing_items = get_clothing_items()
    return render_template('scan.html', user_id=user_id, clothing_items=clothing_items)

# Submit the scan results and redirect to the results page
@app.route('/scan/<user_id>/submit', methods=['POST'])
def submit_scan(user_id):
    # Get the scan results from the request
    cart = request.form.get('cart')
    
    # Ensure cart is a JSON array, not a string
    if isinstance(cart, str):
        try:
            cart_json = json.loads(cart)
        except Exception:
            cart_json = []
    else:
        cart_json = cart
    # Save the scan results to the database
    set_value(user_id, cart_json, "cart")
    return redirect(url_for('factory', user_id=user_id))

# Page where the user is guided to the factory
@app.route('/factory/<user_id>')
def factory(user_id):
    return render_template('factory.html', user_id=user_id)

# Page where the user is guided to the washing machine
@app.route('/washing_machine/<user_id>')
def washing_machine(user_id):
    return render_template('washing_machine.html', user_id=user_id)

# Submit the washing machine results and redirect to the disposal page
@app.route('/washing_machine/<user_id>/submit', methods=['GET'])
def submit_washing_machine(user_id):
    while True:
        # Read the last command from the washing machine
        with open("lastcommand_washingmachine.txt", "r") as f:
            command = f.read()
        if command:
            break
        time.sleep(0.5)
    # Parse the command
    return redirect(url_for('disposal', user_id=user_id))

# Page where the user is guided to the disposal
@app.route('/disposal/<user_id>')
def disposal(user_id):
    return render_template('disposal.html', user_id=user_id)

# Submit the disposal results and redirect to the results page
@app.route('/disposal/<user_id>/submit', methods=['GET'])
def submit_disposal(user_id):
    print("Starting disposal selection")
    ser = serial.Serial('COM12', 9600)
    while True:
        line = ser.readline().decode().strip()
        if line:
            print(line)
            ser.close()
            #TODO: Calculate the results based on the line
            return jsonify({"line": line})
        time.sleep(0.1)

@app.route('/results/<user_id>')
def results(user_id):
    return render_template('results.html', user_id=user_id)

if __name__ == '__main__':
    # Start PyGame visualization in a separate process
    p = Process(target=washingmachine.main)
    p.start()

    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
