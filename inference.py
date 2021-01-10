from flask import Flask, request, render_template, jsonify
import pickle
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = 'secret'

INDEX = ['Weight', 'Zoom_wide', 'Low_resolution', 'Zoom_tele',
     'Dimensions', 'Max_resolution', 'Effective_pixels']

with open('reg.pickle', 'rb') as f:
    MODEL = pickle.load(f)


def make_pred(params):
    df = pd.DataFrame(params, index=INDEX).T
    prediction = MODEL.predict(df)
    return prediction


@app.route('/', methods=['GET'])
def main():
    single = request.args.get('single_pred', default=0)
    multiple = request.args.get('mult_pred', default=0)
    if multiple != 0:
        multiple = eval(multiple)
        mult_len = len(multiple)
    else:
        mult_len = 0

    params = request.args.get('params', default=0)
    par_mult = request.args.get('params_mult', default=0)
    if par_mult != 0:
        par_mult = eval(par_mult)

    return render_template('main.html', single_pred=single, params=params,
                           mult_pred=multiple, params_mult=par_mult, mult_len=mult_len)


@app.route('/predict_single', methods=['GET'])
def predict_single():
    Effective_pixels = request.args.get('Effective pixels', default=0)
    Max_resolution = request.args.get('Max resolution', default=0)
    Dimensions = request.args.get('Dimensions', default=0)
    Zoom_tele = request.args.get('Zoom tele (T)', default=0)
    Low_resolution = request.args.get('Low resolution', default=0)
    Zoom_wide = request.args.get('Zoom wide (W)', default=0)
    Weight = request.args.get('Weight (inc. batteries)', default=0)

    params_list = list([Weight, Zoom_wide, Low_resolution, Zoom_tele,
                        Dimensions, Max_resolution, Effective_pixels])

    prediction = make_pred(params_list)

    return str(prediction[0])


@app.route('/predict_multiple', methods=['POST'])
def predict_multiple():
    my_json = request.get_json()
    my_json = json.loads(my_json)
    for i in my_json:
        Weight = i[0]['Weight (inc. batteries)']
        Zoom_wide = i[0]['Zoom wide (W)']
        Low_resolution = i[0]['Low resolution']
        Zoom_tele = i[0]['Zoom tele (T)']
        Dimensions = i[0]['Dimensions']
        Max_resolution = i[0]['Max resolution']
        Effective_pixels = i[0]['Effective pixels']

        params_list = list([Weight, Zoom_wide, Low_resolution, Zoom_tele,
                        Dimensions, Max_resolution, Effective_pixels])

        prediction = make_pred(params_list)
        i[0]['prediction'] = prediction[0]

    json_data = json.dumps(my_json)
    return json_data


if __name__ == '__main__':
    app.run(debug=True)
    port = os.environ.get('PORT')
    app.run(host='0.0.0.0', port=int(port))
