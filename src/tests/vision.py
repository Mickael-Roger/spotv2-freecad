import zmq
from spotv2_pb2 import Objects

# Initialize ZeroMQ subscriber
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

def process_message(data):
    """ Deserialize the protobuf message and print object details. """
    objects_msg = Objects()
    objects_msg.ParseFromString(data)
    
    for obj in objects_msg.objets:
        print(f"Object: {obj.type} at {obj.proba:.2f} in "
              f"{obj.box.first.x},{obj.box.first.y} to "
              f"{obj.box.last.x},{obj.box.last.y}")

def main():
    print("Listening for object detection messages...")
    while True:
        try:
            message = socket.recv()
            process_message(message)
        except KeyboardInterrupt:
            print("Subscriber stopped.")
            break

if __name__ == "__main__":
    main()
