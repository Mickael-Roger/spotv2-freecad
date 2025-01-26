# Installation

On the raspberry pi, activate PCIe Gen3
```bash
sudo raspi-config
```

Then installa Hailo
```bash
sudo apt install hailo-all
```

Add the video rights to pi user
```bash
usermod -aG video pi
```

Create the Spot directory
```bash
mkdir -p /opt/spotv2
chown -R pi: /op/spotv2
```
