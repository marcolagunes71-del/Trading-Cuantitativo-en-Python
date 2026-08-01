# -*- coding: utf-8 -*-
# Importar librerías
import sys
import os
import string

# Comprobar que nltk está instalado y dar instrucciones si no lo está
try:
    import nltk
except ModuleNotFoundError:
    print("ERROR: El paquete 'nltk' no está instalado en este intérprete.")
    print("Instálalo ejecutando: python -m pip install nltk vaderSentiment")
    print("Si usas Jupyter/Colab, en una celda ejecuta: %pip install -q nltk vaderSentiment")
    sys.exit(1)

# Comprobar que vaderSentiment está instalado y dar instrucciones si no lo está
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # pip install vaderSentiment
except ModuleNotFoundError:
    print("ERROR: El paquete 'vaderSentiment' no está instalado en este intérprete.")
    print("Instálalo ejecutando: python -m pip install vaderSentiment")
    print("Si usas Jupyter/Colab, en una celda ejecuta: %pip install -q vaderSentiment")
    sys.exit(1)

# Función para asegurar recursos de NLTK (punkt, wordnet, stopwords)
def ensure_nltk_resources(lang='english'):
    resources = [
        ('punkt', [f"tokenizers/punkt_tab/{lang}", f"tokenizers/punkt/{lang}", 'tokenizers/punkt']),
        ('wordnet', ['corpora/wordnet']),
        ('stopwords', ['corpora/stopwords']),
    ]

    for res_name, paths in resources:
        found = False
        for p in paths:
            try:
                nltk.data.find(p)
                found = True
                break
            except LookupError:
                continue

        if not found:
            print(f"Recurso NLTK '{res_name}' no encontrado. Intentando descargar '{res_name}'...")
            try:
                ok = nltk.download(res_name, quiet=True)
            except Exception as e:
                print(f"Error al descargar '{res_name}': {e}")
                return False

            if not ok:
                print(f"La descarga de '{res_name}' devolvió False. Comprueba conexión o permisos.")
                return False

            # revalidar
            for p in paths:
                try:
                    nltk.data.find(p)
                    found = True
                    break
                except LookupError:
                    continue

            if not found:
                print(f"No se pudo localizar '{res_name}' tras la descarga. Revisa NLTK_DATA o permisos.")
                return False

    return True

# Intentar asegurar recursos
if not ensure_nltk_resources():
    print("Abortando: faltan recursos de NLTK. Ejecuta manualmente 'nltk.download(...)' si es necesario.")
    sys.exit(1)

# Texto de ejemplo
texto = "Cats love to play with small balls! They are playful and energetic."

# 1) Tokenización: Divide el texto en unidades más pequeñas (tokens), generalmente palabras
tokens = nltk.tokenize.word_tokenize(texto.lower())
print("Tokens:", tokens)

# 2) Lematización: Reduce las palabras a su forma base o lema. Por ejemplo, "cats" se convierte en "cat"
lematizer = nltk.stem.WordNetLemmatizer()
lemmatized_tokens = [lematizer.lemmatize(token) for token in tokens]
print("Lematización:", lemmatized_tokens)

# 3) Steamming: Reduce las palabras a su raíz. Por ejemplo, "playful" se convierte en "play"
stemmer = nltk.stem.PorterStemmer()
stemmed_tokens = [stemmer.stem(token) for token in lemmatized_tokens]
print("Stemming:", stemmed_tokens)

# 4) Eliminación de Stop Words: Elimina palabras comunes que no aportan mucho significado ("in", "is", "the")
stop_words = set(nltk.corpus.stopwords.words("english"))
filtered_tokens = [token for token in stemmed_tokens if token not in stop_words]
print("Tokens sin Stop Words:", filtered_tokens)

# 5) Normalización (remover puntuaciones): Limpia el texto eliminando puntuación, emoticonos y otros caracteres especiales no deados.
normalized_tokens =[token for token in filtered_tokens if token not in string.punctuation]
print("Tokens normalizados:", normalized_tokens)

# Unir tokens en una sola sentencia nuevamente
texto_procesado = " ".join(normalized_tokens)
print(texto_procesado)

# Crear Instancia del Analizador de Sentimiento
sia = SentimentIntensityAnalyzer()

# Obtener Sentimiento
scores = sia.polarity_scores(texto_procesado)
print(scores)

# Validar el sentimiento
if scores["compound"] >= 0:
    print("¡La frase tiene un sentimiento Positivo!")
else:
    print("¡La frase tiene un sentimiento Negativo!")
    
# Analizar el Texto sin Procesamiento Propio
sent_no_procesada = sia.polarity_scores(texto)
print(sent_no_procesada)

# Validar el sentimiento
if sent_no_procesada["compound"] >= 0:
    print("¡La frase tiene un sentimiento Positivo!")
else:
    print("¡La frase tiene un sentimiento Negativo!")

# Recordatorio:
#   - El análisis de sentimiento requiere un procesamiento adecuado del texto para obtener resultados precisos.
#   - El análisis de sentimiento nos ayuda a comprender las opiniones expresadas en el texto proporcionando probabilidades
#     de cómo se siente la gente hacia un tema específico.
