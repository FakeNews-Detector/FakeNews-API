from tensorflow import keras
import re
from keras.preprocessing.text import Tokenizer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import nltk
from nltk.corpus import stopwords
from flask import Flask, request, jsonify
import sqlalchemy
import json

model = keras.models.load_model("lstm_model.h5")
model.load_weights("lstm_weights.h5")

nltk.download('stopwords')
vocab_size = 2000
embedding_dim = 16
max_length = 100
trunc_type = "post"
padding_type = "post"
oov_tok = "<OOV>"

punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
def remove_punctuation(text):
    no_punct = "".join([i for i in text if i not in punc])
    return no_punct


def remove_number(text):
    no_number = re.sub(r'\d', '', text)
    return no_number

factory = StemmerFactory()
stemmer = factory.create_stemmer()

stopword = stopwords.words('indonesian')
stopword.extend(["c", "rp", "di", "ok", "tak", "r", "x", "i", "ini", "jadi", "ada", "ke", "dan", "akan", 
"sang", "yang", "ada", "bagi", "untuk", "pada", "dengan", "saat", "tidak", "nak", "tapi", "buat", "semua",
"dari", "ingin", "gara", "saat", "anak", "hey", "bro"])

def clean_text(text, stem=False):
    tokens = []
    for token in text.split():
        if token not in stopword:
            if stem:
                tokens.append(stemmer.stem(token))
            else:
                tokens.append(token)
    return tokens



def new_predict(text):
  text = text.lower()
  text = remove_punctuation(text)
  text = remove_number(text)
  text = clean_text(text)
  tokenizer = Tokenizer(num_words = vocab_size, oov_token = oov_tok)
  tokenizer.fit_on_texts(text)
  pred = tokenizer.texts_to_sequences(text)
  prediction = model.predict(pred)
  avg_pred = prediction.mean()
  if avg_pred > 0.5:
    text_label = 'Hoax'
  else:
    text_label = 'Valid'
  return text_label, avg_pred

connection_name = "fakenews-detection-352513:asia-southeast2:fakenews-detec"
db_name = "db_fakenews"
db_user = "root"
db_password = "admin"

driver_name = 'mysql+pymysql'
query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    text = data['text']
    text_label, avg_pred = new_predict(text)

    result = {
        "avg_pred": str(avg_pred),
        "text_label": text_label
    }
    return jsonify(result)


@app.route("/getnews", methods=["GET"])
def getnews():
    table_name = "article"
    param = request.args.get('kategori')
    stmt = sqlalchemy.text('SELECT * FROM {}'.format(table_name))

    if param:
        stmt = sqlalchemy.text('SELECT * FROM {} WHERE kategori LIKE "%{}%"'.format(table_name, param))

    db = sqlalchemy.create_engine(
      sqlalchemy.engine.url.URL(
        drivername=driver_name,
        username=db_user,
        password=db_password,
        database=db_name,
        query=query_string,
      ),
      pool_size=5,
      max_overflow=2,
      pool_timeout=30,
      pool_recycle=1800
    )
    try:
        with db.connect() as conn:
            results = conn.execute(stmt)
            return json.dumps( [dict(ix) for ix in results] )
    except Exception as e:
        return 'Error: {}'.format(str(e))


if __name__ == "__main__":
    app.run(debug=True)