import time
import zmq
import threading
from motion_pb2 import Motion, Command, ServoStatus

import datetime

from STservo_sdk import *



# Default setting
BAUDRATE                = 1000000
DEVICENAME              = '/dev/ttyACM0' 

MAX_SPEED = 3000
MAX_ACCEL = 50
MIN_POSITION  = 0
MAX_POSITION  = 4095


SERVOS = {
  "FOOT_LEFT_FRONT": 1,
#  "FOOT_RIGHT_FRONT": 2,
#  "FOOT_LEFT_BACK": 3,
#  "FOOT_RIGHT_BACK": 4,
#  "LEG_LEFT_FRONT": 5,
#  "LEG_RIGHT_FRONT": 6,
#  "LEG_LEFT_BACK": 7,
#  "LEG_RIGHT_BACK": 8,
#  "SHOULDER_LEFT_FRONT": 9,
#  "SHOULDER_RIGHT_FRONT": 10,
#  "SHOULDER_LEFT_BACK": 11,
#  "SHOULDER_RIGHT_BACK": 12
}


class ST3215:

  def __init__(self):
    self.portHandler = PortHandler(DEVICENAME)

    self.packetHandler = sts(self.portHandler)

    if not self.portHandler.openPort():
      raise ValueError(f"Fail to open Servo board port: {DEVICENAME}")


    if not self.portHandler.setBaudRate(BAUDRATE):
      raise ValueError("Failed to set the baudrate")


    for servoId in SERVOS.values():
      sts_model_number, sts_comm_result, sts_error = self.packetHandler.ping(servoId)
      if sts_comm_result != COMM_SUCCESS or sts_error != 0:
        raise ValueError("Could not find servo: %d" % servoId)


    self.context = zmq.Context()


  def read_register(self, servo_id, register, size):
    try:
      if size == 1:
        read_reg = self.packetHandler.read1ByteTxRx
      elif size == 2:
        read_reg = self.packetHandler.read2ByteTxRx
      elif size == 4:
        read_reg = self.packetHandler.read4ByteTxRx
      else:
        return True, None

      val, comm_result, error =  read_reg(servo_id, register)
      if comm_result != COMM_SUCCESS:
        print(self.packetHandler.getTxRxResult(comm_result))
        return True, None

      if error != 0:
        print(self.packetHandler.getRxPacketError(error))
        return True, None

      return False, val

    except: 
      return True, None



  def publish(self):
    socket = self.context.socket(zmq.PUB)
    socket.bind(f"tcp://*:5565")

    motion = Motion()

    while True:

      for servoName, servoId in SERVOS.items():
        servObj = getattr(motion, servoName)
        try:
          error, value = self.read_register(servoId, STS_PRESENT_SPEED_L, 2)
          if error:
            servObj.speed = None
          else:
            servObj.speed = value

          error, value = self.read_register(servoId, STS_PRESENT_POSITION_L, 2)
          if error:
            servObj.position = None
          else:
            servObj.position = value

          error, value = self.read_register(servoId, STS_PRESENT_LOAD_L, 2)
          if error:
            servObj.resistance = None
          else:
            servObj.resistance = value

          error, value = self.read_register(servoId, STS_PRESENT_VOLTAGE, 1)
          if error:
            servObj.voltage = None
          else:
            servObj.voltage = value

          error, value = self.read_register(servoId, STS_PRESENT_CURRENT_L, 2)
          if error:
            servObj.current = None
          else:
            servObj.current = value

          error, value = self.read_register(servoId, STS_PRESENT_TEMPERATURE, 1)
          if error:
            servObj.temp = None
          else:
            servObj.temp = value

        except:
          servObj.status = ServoStatus.ERROR

      serialized_motion = motion.SerializeToString()
      socket.send(serialized_motion)
      time.sleep(0.01)



  def command(self):
    socket = self.context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:5566")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
      message = socket.recv()
      servo_command = ServoCommand()
      servo_command.ParseFromString(message)
      print("Received command:", servo_command)

      for command_item in servo_command.commands:
        if command_item.HasField('move_servo'):
          move_servo = command_item.move_servo
          print(f"Move Servo: ID={move_servo.servo_id}, Position={move_servo.position}, Acceleration={move_servo.acceleration}")
        elif command_item.HasField('stop_servo'):
          stop_servo = command_item.stop_servo
          print(f"Stop Servo: ID={stop_servo.servo_id}")
                # Traitez la commande stop_servo ici...
        elif command_item.HasField('start_servo'):
          start_servo = command_item.start_servo
          print(f"Start Servo: ID={start_servo.servo_id}")
  def __del__(self):
    self.portHandler.closePort()

def main():
  
  motion = ST3215()

  publisher_thread = threading.Thread(target=motion.publish)
  publisher_thread.start()

  subscriber_thread = threading.Thread(target=motion.command)
  subscriber_thread.start()

  publisher_thread.join()
  subscriber_thread.join()


if __name__ == "__main__":
    main()

