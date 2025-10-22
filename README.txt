Suricata Lab (Vagrant)
======================

Topología
---------
- Sx (Ubuntu, 10.0.0.2): IDS Suricata
- Hx (Ubuntu, 10.0.0.3): Servidor web de prueba (login) en :8080
- Kx (Kali,   10.0.0.4): Atacante (hping3, nmap, tcpdump, tshark)

Requisitos
----------
- Vagrant 2.x
- VirtualBox 6.x/7.x (o proveedor compatible)

Puesta en marcha
----------------
1) Coloca estos archivos en una carpeta vacía.
2) Ejecuta:  vagrant up
3) Verifica estado:
   - Hx: http://10.0.0.3:8080  (formulario login; válidas: admin/admin; inválidas -> 401 Unauthorized)
   - Sx: ejecutar Suricata en primer plano sobre la interfaz privada:
         vagrant ssh sx
         sudo suricata -c /etc/suricata/suricata.yaml -i enp0s8 --init-errors-fatal
     (si tu interfaz privada es distinta, ajusta el parámetro -i)
   - Kx: generar tráfico/escaneo:
         vagrant ssh kx
         hping3 -c 1500 -d 60 -S -w 64 -p 80 --flood 10.0.0.3

Notas
-----
- En Sx se configura HOME_NET a "10.0.0.0/24".
- En Hx se despliega un servicio systemd (hx-demo.service) para levantar automáticamente el servidor Flask.
- En Kx se instala hping3/nmap/tcpdump/tshark y se fija la contraseña de root a 'root'.
- Ajusta recursos (CPU/RAM) en el bloque 'provider' si es necesario.
