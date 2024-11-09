install_path := /opt/spotv2

all: build install start

build: protobuf_build gyro_build

install: gyro_install 

start: start_gyro

# Compile all proto files
protobuf_build: $(shell find proto/*.proto -type f)
	protoc --proto_path=./proto/ --python_out=./proto/ ./proto/*.proto
	protoc --proto_path=./proto/ --c_out=./proto/ ./proto/*.proto
	cd ./proto && gcc -c *.c

gyro_build: protobuf_build 
	cd ./gyro && gcc -c DataConverter.c Icm20948AuxCompassAkm.c ICM20948.c Icm20948DataBaseDriver.c Icm20948Dmp3Driver.c Icm20948MPUFifoControl.c Icm20948Setup.c Message.c Icm20948Augmented.c Icm20948AuxTransport.c Icm20948DataBaseControl.c Icm20948DataConverter.c Icm20948LoadFirmware.c Icm20948SelfTest.c Icm20948Transport.c -I../proto
	cd ./gyro && gcc -o gyro DataConverter.o Icm20948AuxCompassAkm.o Icm20948DataBaseControl.o Icm20948DataConverter.o Icm20948LoadFirmware.o ICM20948.o Icm20948Setup.o Message.o Icm20948Augmented.o Icm20948AuxTransport.o Icm20948DataBaseDriver.o Icm20948Dmp3Driver.o     Icm20948MPUFifoControl.o  Icm20948SelfTest.o  Icm20948Transport.o ../proto/*.o -lm -lzmq -lprotobuf-c -I../proto 
	cd ./gyro && rm -rf *.o

gyro_install: gyro_build
	mkdir -p ${install_path}/gyro/
	cp -f ./gyro/gyro ${install_path}/gyro/
	chmod +x ${install_path}/gyro/gyro
	cp -f ./services/gyro.service /etc/systemd/system/spotv2_gyro.service
	systemcl daemon-reload

start_gyro:
	systemctl restart spotv2_gyro


