import paho.mqtt.client as mqtt
import json

BROKER = "broker.hivemq.com"
PORT = 1883
REQUEST_TOPIC = "parking/gate/request"
SUMMARY_TOPIC = "parking/stats/summary"
GATE_TOPIC = "parking/gate/entry"
latest_free_lots = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print("入口道闸已连接，等待车辆到达信号...")
    client.subscribe(REQUEST_TOPIC)
    client.subscribe(SUMMARY_TOPIC)


def on_message(client, userdata, msg):
    global latest_free_lots

    if msg.topic == SUMMARY_TOPIC:
        summary = json.loads(msg.payload.decode())
        latest_free_lots = summary.get("free_lots", 0)
        print(f"道闸同步统计信息: 当前空闲车位 {latest_free_lots}")
        return

    if msg.topic == REQUEST_TOPIC:
        data = json.loads(msg.payload.decode())
        vehicle_id = data.get("vehicle_id", "UNKNOWN")
        if latest_free_lots > 0:
            result = {
                "vehicle_id": vehicle_id,
                "action": "open",
                "message": "允许进入停车场",
            }
            client.publish(GATE_TOPIC, json.dumps(result))
            print(f"道闸已开闸: {vehicle_id} 可以进入")
        else:
            result = {
                "vehicle_id": vehicle_id,
                "action": "wait",
                "message": "当前没有空闲车位，请等待",
            }
            client.publish(GATE_TOPIC, json.dumps(result))
            print(f"道闸保持关闭: {vehicle_id} 需要等待")

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()
