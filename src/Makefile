SHELL := /bin/bash
install_path := /opt/spotv2

all: build install start

build: protobuf_build gyro_build

install: gyro_install vision_install motion_install

start: start_gyro start_vision start_motion

# Compile all proto files
protobuf_build: $(shell find proto/*.proto -type f)
	protoc --proto_path=./proto/ -I/usr/include --python_out=./proto/ ./proto/*.proto
	protoc --proto_path=./proto/ -I/usr/include --c_out=./proto/ ./proto/*.proto
	cd ./proto && gcc -c *.c

gyro_build: protobuf_build 
	cd ./gyro && gcc -c DataConverter.c Icm20948AuxCompassAkm.c ICM20948.c Icm20948DataBaseDriver.c Icm20948Dmp3Driver.c Icm20948MPUFifoControl.c Icm20948Setup.c Message.c Icm20948Augmented.c Icm20948AuxTransport.c Icm20948DataBaseControl.c Icm20948DataConverter.c Icm20948LoadFirmware.c Icm20948SelfTest.c Icm20948Transport.c -I../proto
	cd ./gyro && gcc -o gyro DataConverter.o Icm20948AuxCompassAkm.o Icm20948DataBaseControl.o Icm20948DataConverter.o Icm20948LoadFirmware.o ICM20948.o Icm20948Setup.o Message.o Icm20948Augmented.o Icm20948AuxTransport.o Icm20948DataBaseDriver.o Icm20948Dmp3Driver.o     Icm20948MPUFifoControl.o  Icm20948SelfTest.o  Icm20948Transport.o ../proto/*.o -lm -lzmq -lprotobuf-c -I../proto 
	cd ./gyro && rm -rf *.o

gyro_install: gyro_build
	mkdir -p ${install_path}/gyro/
	cp -f ./gyro/gyro ${install_path}/gyro/
	chmod +x ${install_path}/gyro/gyro
	sudo cp -f ./services/gyro.service /etc/systemd/system/spotv2_gyro.service
	sudo systemctl daemon-reload

vision_install:
	mkdir -p ${install_path}/vision/packages/
	cp -f ./vision/vision.py ./proto/vision_pb2.py ./proto/vision.proto ${install_path}/vision/
	sudo apt install --upgrade  hailort
	virtualenv -p python3.11 ${install_path}/vision/hailo_rpi5
	. ${install_path}/vision/hailo_rpi5/bin/activate && pip3 install ./vision/packages/hailort-4.19.0-cp311-cp311-linux_aarch64.whl
	. ${install_path}/vision/hailo_rpi5/bin/activate && pip3 install -r ./vision/requirements.txt
	sudo cp -f ./services/vision.service /etc/systemd/system/spotv2_vision.service
	sudo systemctl daemon-reload

motion_install:
	mkdir -p ${install_path}/motion/
	cp -rf ./motion/STservo_sdk ./motion/motion.py ./proto/motion_pb2.py ./proto/motion.proto ./motion/requirements.txt ${install_path}/motion/
	virtualenv -p python3.11 ${install_path}/motion/st3215
	. ${install_path}/motion/st3215/bin/activate && pip3 install -r ./motion/requirements.txt
	sudo cp -f ./services/motion.service /etc/systemd/system/spotv2_motion.service
	sudo systemctl daemon-reload


start_motion:
	sudo systemctl restart spotv2_motion

start_gyro:
	sudo systemctl restart spotv2_gyro

start_vision:
	sudo systemctl restart spotv2_vision


