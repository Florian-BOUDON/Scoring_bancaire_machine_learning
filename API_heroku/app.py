from flask import Flask, request, jsonify, send_file
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
import joblib
import pickle
import pandas as pd

df_proba = pd.read_csv('df_stream_proba.csv',index_col="SK_ID_CURR",sep=",")
pipeline= joblib.load('pipeline.pkl')

app = Flask(__name__)


@app.route('/data', methods=['GET'])
def get_data():
    param = request.args.get("proba")
    
    if param is None:
        return jsonify({"error": "Missing parameter 'proba'"}), 400
    
    try:
        param = int(param)
    except ValueError:
        return jsonify({"error": "Invalid parameter 'proba'"}), 400
    
    if param not in df_proba.index:
        return jsonify({"error": "Invalid parameter value for 'proba'"}), 400
    
    p = df_proba.loc[param].to_dict()
    return jsonify(p), 200



# Définir l'endpoint POST
@app.route('/prediction', methods=['POST'])
def prediction():
    # Récupérer le dictionnaire JSON à partir de la requête
    data = request.get_json()

     # Vérifier si le JSON est présent et contient 30 clés
    if data is None or len(data) != 30:
        return jsonify({'error': 'Invalid JSON or incorrect number of keys'}), 400
    
    # Créer un DataFrame à partir du dictionnaire JSON
    df = pd.DataFrame([data])

    # Effectuer la prédiction en utilisant le pipeline
    try:
        proba = pipeline.predict_proba(df)[0][0]
        proba = float(proba)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Renvoyer la réponse sous forme de JSON
    response = {'probability': proba}
    return jsonify(response), 200


# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)