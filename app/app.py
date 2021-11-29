import json
import pickle
import numpy as np
from flask import Flask, request

flask_app = Flask(__name__)

#ML model path
model_path = "model/model.pkl"

@flask_app.route('/', methods=['GET'])
def index_page():
    return_data = {
        "error" : "0",
        "message" : "Successful"
    }
    return flask_app.response_class(response=json.dumps(return_data), mimetype='application/json')

@flask_app.route('/predict',methods=['GET'])
def model_deploy():
    try:
        # Get form values
        age = request.form.get('age')
        sex = request.form.get('sex')
        bmi = request.form.get('bmi')
        bp = request.form.get('bp')
        s1 = request.form.get('s1')
        s2 = request.form.get('s2')
        s3 = request.form.get('s3')
        s4 = request.form.get('s4')
        s5 = request.form.get('s5')
        s6 = request.form.get('s6')

        fields = [age, sex, bmi, bp, s1, s2, s3, s4, s5, s6]

        if not None in fields:
            # Convert the values to float
            age = float(age)
            sex = float(sex)
            bmi = float(bmi)
            bp = float(bp)
            s1 = float(s1)
            s2 = float(s2)
            s3 = float(s3)
            s4 = float(s4)
            s5 = float(s5)
            s6 = float(s6)

            result = [age, sex, bmi, bp, s1, s2, s3, s4, s5, s6]

            # Load the model from disk
            model = pickle.load(open(model_path, 'rb'))

            # Pass values to the model
            prediction = model.predict([result])

            return_data = {
                "error" : '0',
                "message" : 'Successfull',
                "prediction": prediction[0]
            }
        else:
            return_data = {
                "error" : '1',
                "message": "Invalid Parameters"
            }
    except Exception as e:
        return_data = {
            'error' : '2',
            "message": str(e)
            }
    return flask_app.response_class(response=json.dumps(return_data), mimetype='application/json')


if __name__ == "__main__":
    flask_app.run(host ='0.0.0.0',port=9091, debug=False)
