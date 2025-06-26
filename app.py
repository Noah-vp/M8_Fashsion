from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
import serial # type: ignore
from utils.records_management import set_username, set_value, get_value, get_clothing_items
import threading
import time
from multiprocessing import Process

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # Use a strong, random value in production!

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
    print(request.form)
    score = request.form.get('score')
    print(f"Score: {score}")
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
    # From each item, get the total impact and add it to the total impact
    total_impact = {"carbon_footprint": 0, "energy_usage": 0, "water_usage": 0}
    for item in cart_json:
        total_impact["carbon_footprint"] += item["total_impact"]["carbon_footprint"]
        total_impact["energy_usage"] += item["total_impact"]["energy_usage"]
        total_impact["water_usage"] += item["total_impact"]["water_usage"]
    # Save the total impact to the database
    set_value(user_id, total_impact, "factory_impact")
    return redirect(url_for('factory', user_id=user_id))

# Page where the user is guided to the factory
@app.route('/factory/<user_id>')
def factory(user_id):
    # Get the factory_impact from the database
    factory_impact = get_value(user_id, "factory_impact")
    print(f"Factory impact: {factory_impact}")
    # Refactor into a different format
    command = f"{factory_impact['water_usage']}|{factory_impact['carbon_footprint']}"
    print(f"Command: {command}")

    # Send the command to the factory machine
    ser = serial.Serial('COM15', 9600)
    ser.write(command.encode())
    ser.close()

    return render_template('factory.html', user_id=user_id, factory_impact=factory_impact)

# Page where the user is guided to the washing machine
@app.route('/washing_machine/<user_id>')
def washing_machine(user_id):
    return render_template('washing_machine.html', user_id=user_id)

# Submit the washing machine results and redirect to the disposal page
@app.route('/washing_machine/<user_id>/submit', methods=['POST'])
def submit_washing_machine(user_id):
    print("Starting washing machine submission")
    while True:
        # Read the last command from the washing machine
        with open("db/lastcommand_wash.txt", "r") as f:
            command = f.read()
        if command.startswith("N|"):
            with open("db/lastcommand_wash.txt", "w") as f:
                f.write("")
            # Save the command to the database
            set_value(user_id, command.replace("N|", "").split(","), "washing_machine_impact")
            print(f"Command: {command}")
            break
        time.sleep(0.5)
    # Parse the command
    return jsonify({"command": command})

# Page where the user is guided to the disposal
@app.route('/disposal/<user_id>')
def disposal(user_id):
    return render_template('disposal.html', user_id=user_id)

# Submit the disposal results and redirect to the results page
@app.route('/disposal/<user_id>/submit', methods=['GET'])
def submit_disposal(user_id):
    print("Starting disposal selection")
    ser = serial.Serial('COM16', 9600)
    while True:
        line = ser.readline().decode().strip()
        if line:
            print(line)
            ser.close()
            # Save the line to the database
            set_value(user_id, line, "disposal")
            #TODO: Calculate the results based on the line
            return jsonify({"line": line})
        time.sleep(0.1)

@app.route('/results/<user_id>')
def results(user_id):

    return render_template('results.html', user_id=user_id)

def run_washing_machine():
    """Function to run the washing machine visualization in a separate process"""
    import washingmachine
    # The washingmachine module will run its main loop when imported

def run_counter():
    """Function to run the counter visualization in a separate process"""
    import counter
    # The counter module will run its main loop when imported

if __name__ == '__main__':
    # Start PyGame visualization in a separate process
    # p = Process(target=run_washing_machine)
    # p.start()

    # p2 = Process(target=run_counter)
    # p2.start()

    # try:
        # Start Flask app (disable reloader to avoid issues with multiprocessing)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False, ssl_context=("cert.pem", "key.pem"))
    # finally:
        # Ensure PyGame processes are terminated when Flask exits
        # print("Terminating processes...")
        # p.terminate()
        # p2.terminate()
        # p.join()
        # p2.join()
        # print("Cleanup complete")
