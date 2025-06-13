.. role:: red
.. role:: green
.. role:: blue
.. role:: bold

===============================
📊 Forex Price Prediction App
===============================

:blue:`Forex Forecasting Dashboard` est une plateforme complète d’analyse et de prédiction des mouvements de prix du marché des changes (**Forex**) avec une interface conviviale construite sous **Streamlit**.

----

📸 Aperçu du tableau de bord
-----------------------------

.. image:: _static/logo.png
   :alt: Tableau de bord principal
   :align: center
   :width: 80%

----

🎬 Démonstration Vidéo
-----------------------

.. raw:: html

   <video width="750" height="422" controls>
     <source src="_static/video.mp4" type="video/mp4">
     Votre navigateur ne supporte pas les vidéos HTML5.
   </video>

----

🚀 Fonctionnalités Clés
-----------------------

:green:`✔` Récupération des données Forex via **Alpha Vantage**  
:green:`✔` Prévision des prix avec **Facebook Prophet**  
:green:`✔` Affichage des indicateurs techniques : *RSI*, *MACD*, *Bollinger Bands*  
:green:`✔` Signaux de trading avec points d'entrée, TP et SL  
:green:`✔` Intégration des actualités avec analyse de sentiment (News API + TextBlob)  
:green:`✔` Exportation CSV et graphiques interactifs **Plotly**

----

📦 Installation
---------------

1. Cloner le dépôt :
   .. code-block:: bash

      git clone <repository-url>
      cd quant-model-for-forex-predict-prediction

2. Installer les dépendances :
   .. code-block:: bash

      pip install -r requirements.txt
      pip install textblob
      python -m textblob.download_corpora

3. Créer un fichier `.env` :

   .. code-block:: text

      ALPHA_VANTAGE_API_KEY=your_alpha_key
      NEWS_API_KEY=your_news_key

----

▶️ Lancer le Dashboard
----------------------

.. code-block:: bash

   streamlit run app.py

Une interface conviviale s’ouvre dans votre navigateur.

----

📘 Guide Complet
----------------

.. toctree::
   :maxdepth: 2
   :caption: Table des matières

   

----

🔖 Licence
----------

Distribué sous la licence :bold:`MIT`.

----

🙏 Remerciements
----------------

- :blue:`Alpha Vantage` — pour les données Forex
- :blue:`News API` — pour les articles d’actualité
- :blue:`Facebook Prophet` — pour la modélisation temporelle
- :blue:`Streamlit` — pour le tableau de bord interactif
- :blue:`TextBlob` — pour l’analyse de sentiment
