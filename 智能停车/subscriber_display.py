import paho.mqtt.client as mqtt
import os

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "parking/lot/+/status"  # 订阅所有车位状态

# 用于存储各车位最新状态
parking_status = {}

def on_connect(client, userdata, flags, rc):
    print("连接成功，正在监听车位状态...")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    # 从topic中提取lot_id，例如 parking/lot/A01/status
    lot_id = topic.split('/')[2]
    parking_status[lot_id] = payload
    # 清屏并重新打印（模拟实时刷新大屏）
    os.system('cls' if os.name == 'nt' else 'clear')
    print("========== 智能停车场管理大屏 ==========")
    print("车位 | 状态")
    print("-----------------")
    for lot in sorted(parking_status.keys()):
        status_icon = "🟢 空闲" if parking_status[lot] == "free" else "🔴 占用"
        print(f"{lot}  | {status_icon}")
    total_free = sum(1 for s in parking_status.values() if s == "free")
    print("-----------------")
    print(f"空闲车位总数: {total_free}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()