import paho.mqtt.client as mqtt
import json
import time

BROKER = "broker.hivemq.com"
PORT = 1883
SUB_TOPIC = "parking/lot/+/status"
PUB_TOPIC = "parking/stats/summary"
LOTS = [f"A{str(i).zfill(2)}" for i in range(1, 6)]

parking_status = {lot: "unknown" for lot in LOTS}

def on_connect(client, userdata, flags, reason_code, properties):
    print("统计服务已连接")
    client.subscribe(SUB_TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topic
    lot_id = topic.split('/')[2]
    status = msg.payload.decode()
    parking_status[lot_id] = status
    # 计算空闲总数并发布
    total_free = sum(1 for s in parking_status.values() if s == "free")
    total_unknown = sum(1 for s in parking_status.values() if s == "unknown")
    summary = {
        "total_lots": len(LOTS),
        "free_lots": total_free,
        "occupied_lots": len(LOTS) - total_free - total_unknown,
        "unknown_lots": total_unknown,
        "timestamp": time.time()
    }
    client.publish(PUB_TOPIC, json.dumps(summary))
    print(f"已发布统计信息: {summary}")

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()
