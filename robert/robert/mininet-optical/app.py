from flask import Flask, render_template, request, jsonify
import sys

for path in sys.path:
    print(path)

import os

# 确保添加包含 'mnoptical' 的整个目录到 sys.path
sys.path.append(os.path.abspath('/home/wayne/robert/mininet-optical/'))
sys.path.append(os.path.abspath('/home/wayne/robert/mininet-optical/mnoptical/examples/'))
# 尝试导入模块
from mnoptical.dataplane import km, m, dB, dBm



import simulate
import unilinear2S

import asyncio

import logging
from pathlib import Path
app = Flask(__name__)

async def run_unilinear2(span, roadm_insertion_loss, numAmp, boost_target_gain, ber, isTest=True):
    process = await asyncio.create_subprocess_shell(
        f'sudo python3 mnoptical/examples/unilinear2.py {span} {roadm_insertion_loss} {numAmp} {boost_target_gain} {ber}{" test" if isTest else ""}', 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = await process.communicate()

    if process.returncode == 0:
        print('Done.')
    else:
        print('Error.')

async def run_simulate(span, roadm_insertion_loss, numAmp, boost_target_gain, ber):
    process = await asyncio.create_subprocess_shell(
        f'sudo python3 mnoptical/examples/simulate.py {span} {roadm_insertion_loss} {numAmp} {boost_target_gain} {ber}', 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = await process.communicate()

    if process.returncode == 0:
        print('Done.')
    else:
        print('Error.')

@app.route("/")
def initial():
    return render_template("index.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/submit_form", methods=["POST"])
def submit_form():
    try:
        span = int(request.form.get('span', 100))
        roadm_insertion_loss = int(request.form.get('roadm_insertion_loss', 100))
        numAmp = int(request.form.get('numAmp', 100))
        boost_target_gain = int(request.form.get('boost_target_gain', 100))
    except:
        logging.warning(' Input date error.')
        span, roadm_insertion_loss, numAmp, boost_target_gain = 150, 18, 8, 18
    default_ber = 0.05
    ber = request.form.get('BER', None)
    if ber:
        try: 
            ber = float(ber)

        except ValueError:
             ber = default_ber
    else:
        ber = default_ber

    # render new page
    if request.form['submit_btn'] == "do_unilinear2":
        print('enter')
        asyncio.run(run_unilinear2(span, roadm_insertion_loss, numAmp, boost_target_gain, ber, isTest=True))
        # unilinear2.run_unilinear2(span, roadm_insertion_loss, numAmp, boost_target_gain, isTest=True)

        file_path = r'/home/wayne/robert/mininet-optical/result1.txt'  
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                # Step 2: Parse each line
                parts = line.strip().split(' ')
                if len(parts) > 1:
                    data.append(parts)

        print('data: ', data)
        boost_target_gain = [d[0] for d in data]  
        numAmp = [d[1] for d in data]  
        t1_gOSNR = [d[2] for d in data]  
        t2_gOSNR = [d[3] for d in data] 
        t1_BER = [d[4] for d in data]  
        t2_BER = [d[5] for d in data] 

        return render_template('result1.html', boost_target_gain=boost_target_gain, 
                           numAmp=numAmp, 
                           t1_gOSNR=t1_gOSNR, 
                           t2_gOSNR=t2_gOSNR, 
                           t1_BER=t1_BER, 
                           t2_BER=t2_BER)
    
    if request.form['submit_btn'] == "do_simulate":
        print('enter')
        asyncio.run(run_simulate(span, roadm_insertion_loss, numAmp, boost_target_gain, ber))
        # simulate.run_simulate(span, roadm_insertion_loss, numAmp, boost_target_gain, ber)
        file_path = r'/home/wayne/robert/mininet-optical/result2.txt'  
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                # Step 2: Parse each line
                parts = line.strip().split(' ')
                if len(parts) > 1:
                    data.append(parts)
        boost_target_gain = [d[0] for d in data]  
        numAmp = [d[1] for d in data]  
        t1_gOSNR = [d[2] for d in data]  
        t2_gOSNR = [d[3] for d in data] 
        t1_BER = [d[4] for d in data]  
        t2_BER = [d[5] for d in data] 
        
        recommend = list(range(1, len(data) + 1))

        return render_template('result2.html', recommend=recommend, boost_target_gain=boost_target_gain, 
                               numAmp=numAmp, t1_gOSNR=t1_gOSNR, t2_gOSNR=t2_gOSNR, t1_BER=t1_BER, t2_BER=t2_BER)


@app.route("/result1")
def result1():
    return render_template("result1.html")

@app.route("/result2")
def result2():
    return render_template("result2.html")

import subprocess

@app.route('/run_mininet')
def run_mininet():
    try:
        # Example Mininet command
        result = subprocess.check_output(['sudo', 'mn', '--test', 'pingall'], stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.output.decode('utf-8')}"


if __name__ == "__main__":    
    # app.run(debug=True)
    app.run(host="0.0.0.0", port="5001", debug=False)
    