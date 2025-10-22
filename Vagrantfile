# -*- mode: ruby -*-
# vi: set ft=ruby :

# Suricata Lab: 3 VMs (Sx: Suricata/Ubuntu, Hx: Victim/Ubuntu with web server, Kx: Kali attacker)
# Network:
#   NAT (default) + private network 10.0.0.0/24
#   Sx: 10.0.0.2  Hx: 10.0.0.3  Kx: 10.0.0.4
# Credentials created:
#   Ubuntu (Sx/Hx): user 'suri' / pass 'seca1234' (sudo enabled)
#   Kali (Kx): sets root password to 'root'
#
# Provider: VirtualBox (tweak CPU/RAM as needed).

Vagrant.configure("2") do |config|
  # Global defaults
  config.vm.box_check_update = false
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # -------- Sx: Suricata sensor (Ubuntu) --------
  config.vm.define "sx" do |sx|
    sx.vm.hostname = "Sx"
    sx.vm.box = "ubuntu/jammy64"
    sx.vm.network "private_network", ip: "10.0.0.2"

    sx.vm.provider "virtualbox" do |vb|
      vb.name = "suricata-sx"
      vb.cpus = 2
      vb.memory = 2048
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    end

    sx.vm.provision "shell", inline: <<-SHELL
      set -eux
      export DEBIAN_FRONTEND=noninteractive
      apt-get update -y
      apt-get install -y software-properties-common apt-transport-https ca-certificates curl gnupg lsb-release
      # OISF PPA for latest stable Suricata
      add-apt-repository -y ppa:oisf/suricata-stable
      apt-get update -y
      apt-get install -y suricata tcpdump jq
      # Create user 'suri'
      if ! id -u suri >/dev/null 2>&1; then
        useradd -m -s /bin/bash suri
        echo 'suri:seca1234' | chpasswd
        usermod -aG sudo suri
      fi
      # Basic Suricata tuning: set HOME_NET and default interface
      # Detect the private interface (the non-NAT one)
      IFACE=$(ip -o -4 route show to 10.0.0.0/24 | awk '{print $3}' | head -n1 || true)
      if [ -z "$IFACE" ]; then IFACE="enp0s8"; fi
      # Backup config
      cp /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bak
      # Set HOME_NET
      sed -i 's#HOME_NET:.*#HOME_NET: "[10.0.0.0/24]"#' /etc/suricata/suricata.yaml
      # Ensure logging to /var/log/suricata (default) and enable eve.json if not already
      if ! grep -q 'eve-log:' /etc/suricata/suricata.yaml; then
        printf "\\neve-log:\\n  enabled: yes\\n  filetype: regular\\n  filename: eve.json\\n" >> /etc/suricata/suricata.yaml
      fi
      # Enable service but stop it (lab runs in foreground typically)
      systemctl enable suricata
      systemctl stop suricata || true
      echo "Sx ready. To run in foreground on interface $IFACE:"
      echo "  sudo suricata -c /etc/suricata/suricata.yaml -i $IFACE --init-errors-fatal"
    SHELL
  end

  # -------- Hx: Victim (Ubuntu) with simple web server on :8080 --------
  config.vm.define "hx" do |hx|
    hx.vm.hostname = "Hx"
    hx.vm.box = "ubuntu/jammy64"
    hx.vm.network "private_network", ip: "10.0.0.3"

    hx.vm.provider "virtualbox" do |vb|
      vb.name = "suricata-hx"
      vb.cpus = 2
      vb.memory = 1536
    end

    hx.vm.provision "file", source: "server.py", destination: "/tmp/server.py"

    hx.vm.provision "shell", inline: <<-SHELL
      set -eux
      export DEBIAN_FRONTEND=noninteractive
      apt-get update -y
      apt-get install -y python3 python3-pip
      # Create user 'suri'
      if ! id -u suri >/dev/null 2>&1; then
        useradd -m -s /bin/bash suri
        echo 'suri:seca1234' | chpasswd
        usermod -aG sudo suri
      fi
      pip3 install --no-input flask waitress
      install -o suri -g suri -m 0644 /tmp/server.py /home/suri/server.py

      # systemd service for the demo web server (port 8080)
      cat >/etc/systemd/system/hx-demo.service <<'UNIT'
[Unit]
Description=HX Demo Login Web (Flask)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=suri
WorkingDirectory=/home/suri
ExecStart=/usr/bin/python3 /home/suri/server.py 8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

      systemctl daemon-reload
      systemctl enable hx-demo.service
      systemctl restart hx-demo.service
      echo "Hx ready at http://10.0.0.3:8080"
    SHELL
  end

  # -------- Kx: Attacker (Kali) --------
  config.vm.define "kx" do |kx|
    kx.vm.hostname = "Kx"
    kx.vm.box = "kalilinux/rolling"
    kx.vm.network "private_network", ip: "10.0.0.4"

    kx.vm.provider "virtualbox" do |vb|
      vb.name = "suricata-kx"
      vb.cpus = 2
      vb.memory = 2048
    end

    kx.vm.provision "shell", inline: <<-SHELL
      set -eux
      export DEBIAN_FRONTEND=noninteractive
      apt-get update -y
      apt-get install -y hping3 nmap tcpdump tshark
      # Set root password to 'root' (to match lab instructions)
      echo -e "root\nroot" | passwd root
      echo "Kx ready. Examples:"
      echo "  hping3 -c 1500 -d 60 -S -w 64 -p 80 --flood 10.0.0.3"
    SHELL
  end
end
