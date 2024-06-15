from flask import Flask,url_for,render_template
import os

app=Flask(__name__)


@app.route('/'):
    
def home():
    render_template('index.html')


if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
    