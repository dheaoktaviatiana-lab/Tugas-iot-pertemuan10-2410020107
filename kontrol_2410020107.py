import time
import random
import threading
import paho.mqtt.client as mqtt

NIM = "2410020107"

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_CLIENT_ID = f"Perangkat-{NIM}"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

INTERVAL_PUBLISH = 3  # kirim suhu setiap 3 detik


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Berhasil terhubung ke broker!")
        client.subscribe(TOPIC_RELAY, qos=0)
        client.subscribe(TOPIC_PWM, qos=0)
        print(f"[MQTT] Menunggu perintah di {TOPIC_RELAY} dan {TOPIC_PWM}")
    else:
        print(f"[MQTT] Gagal terhubung, kode: {rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8").strip()
    print(f"[MQTT] Pesan masuk [{msg.topic}]: {payload}")

    if msg.topic == TOPIC_RELAY:
        if payload == "ON":
            print("[GPIO 26 - RELAY] MENYALA (HIGH)")
        elif payload == "OFF":
            print("[GPIO 26 - RELAY] MATI (LOW)")
        else:
            print(f"[GPIO 26 - RELAY] Perintah tidak dikenal: {payload}")

    elif msg.topic == TOPIC_PWM:
        try:
            nilai = max(0, min(255, int(float(payload))))
            print(f"[GPIO 2 - PWM LED] Kecerahan diatur ke {nilai}/255")
        except ValueError:
            print(f"[GPIO 2 - PWM LED] Nilai PWM tidak valid: {payload}")


def baca_suhu_dht22():
    return round(random.uniform(25.0, 30.0), 2)


def publish_loop(client):
    while True:
        suhu = baca_suhu_dht22()
        client.publish(TOPIC_SUHU, str(suhu), qos=0)
        print(f"[DHT22] Kirim suhu ke {TOPIC_SUHU} -> {suhu} °C")
        time.sleep(INTERVAL_PUBLISH)


def main():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
    time.sleep(1)

    t = threading.Thread(target=publish_loop, args=(client,), daemon=True)
    t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Program berhenti.")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()