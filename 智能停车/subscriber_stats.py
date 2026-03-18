import paho.mqtt.client as mqtt
import json

BROKER = "broker.hivemq.com"
PORT = 1883
SUB_TOPIC = "parking/lot/+/status"
PUB_TOPIC = "parking/stats/summary"

parking_status = {}

def on_connect(client, userdata, flags, rc):
    print("统计服务已连接")
    client.subscribe(SUB_TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topic
    lot_id = topic.split('/')[2]
    status = msg.payload.decode()
    parking_status[lot_id] = status
    # 计算空闲总数并发布
    total_free = sum(1 for s in parking_status.values() if s == "free")
    summary = {
        "total_lots": len(parking_status),
        "free_lots": total_free,
        "occupied_lots": len(parking_status) - total_free,
        "timestamp": time.time()
    }
    client.publish(PUB_TOPIC, json.dumps(summary))
    print(f"已发布统计信息: {summary}")

if __name__ == "__main__":
    import time
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()