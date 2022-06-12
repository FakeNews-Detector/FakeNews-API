# FakeNews-API
In this project the Cloud Computing team did several things including:
1. Create a local database about various kinds of news.
2. Create an API where there are 2 functions, namely the getNews function with an endpoint (GET) which can display news from the previous database and a predict function with an endpoint (post) which can make predictions based on a model that has been created by the machine learning team.

In using GCP (Google Cloud Platform) we use:
1. SQL to connect local database with project in GCP.
2. cloud run to deploy the API that was previously created by calling the API and some files from the github repository and local database connected to the GCP SQL project.

For API Requests:
1. getNews : [{"idarticle": 1 , "judul": "Ditemukan Putri duyung", "gambar": "lorem.jpg", "isiarticle": "lorem ipsum lorem ipsum", "deskripsi": "Lorem ipsum", "kategori": "Dunia"}]
2. predict : {"text": "Pemakaian Masker Menyebabkan Penyakit Legionnaires"} 
