import paho.mqtt.client as mqtt
import os

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "parking/lot/+/status"  # 订阅所有车位状态
LOTS = [f"A{str(i).zfill(2)}" for i in range(1, 6)]

# 用于存储各车位最新状态
parking_status = {lot: "unknown" for lot in LOTS}

def on_connect(client, userdata, flags, reason_code, properties):
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
        if parking_status[lot] == "free":
            status_icon = "🟢 空闲"
        elif parking_status[lot] == "occupied":
            status_icon = "🔴 占用"
        else:
            status_icon = "🟡 未更新"
        print(f"{lot}  | {status_icon}")
    total_free = sum(1 for s in parking_status.values() if s == "free")
    total_unknown = sum(1 for s in parking_status.values() if s == "unknown")
    print("-----------------")
    print(f"空闲车位总数: {total_free}")
    print(f"未上报车位数: {total_unknown}")

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()
