import tweepy
import mysql.connector
import random
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

def db_connection():
    db_config = {
        "host": os.getenv("HOST"),
        "user": os.getenv("USER"),
        "password": os.getenv("PASSWORD"),
        "database": os.getenv("DATABASE")
    }
    connection = mysql.connector.connect(**db_config)
    return connection


def obtener_tweet_aleatorio():
    try:
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, contenido FROM tweets WHERE estado = 'aprobado'")
        tweets_aprobados = cursor.fetchall()
        total_tweets = len(tweets_aprobados)

        if total_tweets == 0:
            print("No hay tweets aprobados disponibles en la base de datos.")
            return None

        random_tweet = random.choice(tweets_aprobados)

        cursor.close()
        return random_tweet

    except Exception as e:
        print(f"Error al obtener un tweet aleatorio: {e}")
        return None


def publicar_tweet(tweet):
    try:
        client = tweepy.Client(os.getenv("X_BEARER_TOKEN"),
                               os.getenv("X_CONSUMER_KEY"),
                               os.getenv("X_CONSUMER_SECRET"),
                               os.getenv("X_ACCESS_TOKEN"),
                               os.getenv("X_ACCESS_TOKEN_SECRET"))

        tweet_id, tweet_text = tweet
        client.create_tweet(text = tweet_text)

        connection = db_connection()
        cursor = connection.cursor()
        fecha_publicacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        fecha_publicacion_datetime = datetime.now() - timedelta(hours=5)
        fecha_publicacion = fecha_publicacion_datetime.strftime("%Y-%m-%d %H:%M:%S")

        #cursor.execute("UPDATE tweets SET estado = 'posteado', fechaPost = %s WHERE id = %s",(fecha_publicacion, tweet_id))
        connection.commit()
        cursor.close()

        print(f"Tweet con ID {tweet_id} publicado con éxito y actualizado en la base de datos!")

    except Exception as e:
        print(f"Error al publicar el tweet: {e}")


if __name__ == "__main__":

    horas_ejecucion = ["14:20", "18:20", "00:20", "05:20"]
    hora_actual = datetime.now().strftime("%H:%M")

    if hora_actual in horas_ejecucion:
        segundos = random.uniform(2 * 60, 5 * 60)
        time.sleep(segundos)
        load_dotenv()
        try:
            tweet = obtener_tweet_aleatorio()
            if tweet:
                publicar_tweet(tweet)
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
