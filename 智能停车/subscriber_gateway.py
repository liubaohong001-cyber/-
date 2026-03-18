import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
GATE_TOPIC = "parking/gate/entry"

def on_connect(client, userdata, flags, rc):
    print("入口道闸已连接，等待车辆到达信号...")
    # 实际中可能订阅某个车辆检测主题，这里简单示例直接发布开门指令
    # 模拟车辆到达：每10秒自动发一次开门
    import threading
    def auto_open():
        while True:
            time.sleep(10)
            client.publish(GATE_TOPIC, "open")
            print("道闸控制: 发送开门指令")
    threading.Thread(target=auto_open, daemon=True).start()

if __name__ == "__main__":
    import time
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    client.loop_forever()