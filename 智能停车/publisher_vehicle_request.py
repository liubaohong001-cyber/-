import json
import random
import time

import paho.mqtt.client as mqtt


BROKER = "broker.hivemq.com"
PORT = 1883
REQUEST_TOPIC = "parking/gate/request"
VEHICLE_IDS = ["CAR-101", "CAR-102", "CAR-205", "CAR-309"]


if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    print("等待车位统计服务稳定后，再开始发送车辆请求...")
    time.sleep(10)

    while True:
        vehicle_id = random.choice(VEHICLE_IDS)
        payload = {
            "vehicle_id": vehicle_id,
            "request_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        client.publish(REQUEST_TOPIC, json.dumps(payload))
        print(f"车辆入场请求已发送: {payload}")
        time.sleep(random.randint(8, 15))
