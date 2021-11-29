import json
import pickle
from flask import Flask, request
from datarobot.mlops.mlops import MLOps
import time
import pandas as pd

# Add MLOps Agent
DEPLOYMENT_ID = '61924d543e5e9828d5c5e84d'
MODEL_ID = '61924d3510fc1c63d820b4c8'
# Spool directory path must match the Monitoring Agent path configured by admin.
#SPOOL_DIR = "/tmp/ta"
QUEUE_URL = "amqp://localhost"
QUEUE_NAME = "mlops"
# MLOPS: initialize the MLOps instance
mlops = MLOps() \
    .set_deployment_id(DEPLOYMENT_ID) \
    .set_model_id(MODEL_ID) \
    .set_rabbitmq_spooler(QUEUE_URL, QUEUE_NAME)

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
            start_time = time.time()
            prediction = model.predict([result])
            end_time = time.time()

            # MLOPS: report the number of predictions in the request and the execution time.
            mlops.report_deployment_stats(1, end_time - start_time)

            # MLOPS: report the predictions data: features, predictions, class_names
            feature_data = {
                "age": [age],
                "sex": [sex],
                "bmi": [bmi],
                "bp": [bp],
                "s1": [s1],
                "s2": [s2],
                "s3": [s3],
                "s4": [s4],
                "s5": [s5],
                "s6": [s6]
            }

            features_df = pd.DataFrame.from_dict(feature_data)

            mlops.report_predictions_data(features_df=features_df, predictions=prediction.tolist())

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
    mlops.init()
    flask_app.run(host ='0.0.0.0',port=9091, debug=True)
    #mlops.shutdown()
