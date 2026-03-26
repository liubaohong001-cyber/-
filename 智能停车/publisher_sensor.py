import paho.mqtt.client as mqtt
import time
import random
import threading

# MQTT Broker配置（使用公共HiveMQ）
BROKER = "broker.hivemq.com"
PORT = 1883
BASE_TOPIC = "parking/lot"

# 模拟5个车位
LOTS = [f"A{str(i).zfill(2)}" for i in range(1, 6)]

def sensor_simulator(lot_id):
    """每个车位独立线程模拟传感器"""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    topic = f"{BASE_TOPIC}/{lot_id}/status"
    while True:
        # 随机生成状态：70%概率空闲，30%概率占用（模拟真实场景）
        status = random.choices(["free", "occupied"], weights=[0.7, 0.3])[0]
        client.publish(topic, status)
        print(f"[{lot_id}] 发布状态: {status}")
        time.sleep(random.randint(3, 8))  # 随机间隔3-8秒

if __name__ == "__main__":
    threads = []
    for lot in LOTS:
        t = threading.Thread(target=sensor_simulator, args=(lot,))
        t.daemon = True
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
