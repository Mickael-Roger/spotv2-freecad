import cv2
import numpy as np
import hailo
import zmq
import time
from spotv2_pb2 import Objects, Object, Box, Position

MODEL_PATH = "/usr/share/rpi-camera-assets/hailo_yolov8_inference.json"
cam_index = 0
MAX_FPS = 10

# Initialize ZeroMQ publisher
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

def load_model(model_path):
    device = hailo.HailoDevice()
    network_group = device.load_network_group(model_path)
    return network_group

def preprocess_frame(frame, input_shape):
    resized_frame = cv2.resize(frame, (input_shape[1], input_shape[0]))
    normalized_frame = resized_frame / 255.0
    return normalized_frame.astype(np.float32)

def infer_frame(network_group, frame):
    input_tensor = preprocess_frame(frame, (640, 640, 3))
    input_tensor = np.expand_dims(input_tensor, axis=0)
    infer_result = network_group.run({'input': input_tensor})
    return infer_result['output']

def publish_detections(results):
    objects_msg = Objects()
    objects_msg.timestamp = int(time.time())
    
    for result in results:
        x1, y1, x2, y2, confidence, class_id = result
        if confidence > 0.5:  # Confidence threshold
            obj_msg = Object()
            obj_msg.box.first.x = int(x1)
            obj_msg.box.first.y = int(y1)
            obj_msg.box.last.x = int(x2)
            obj_msg.box.last.y = int(y2)
            obj_msg.type = str(class_id)
            obj_msg.proba = float(confidence)
            objects_msg.objets.append(obj_msg)
    
    socket.send(objects_msg.SerializeToString())

def main():
    network_group = load_model(MODEL_PATH)
    cap = cv2.VideoCapture(cam_index)

    if not cap.isOpened():
        print("Error: Unable to open camera")
        return

    frame_time = 1.0 / MAX_FPS
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        results = infer_frame(network_group, frame)
        publish_detections(results)
        
        elapsed_time = time.time() - start_time
        sleep_time = max(0, frame_time - elapsed_time)
        time.sleep(sleep_time)

    cap.release()

if __name__ == "__main__":
    main()



