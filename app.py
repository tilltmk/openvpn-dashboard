from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import subprocess
import os

app = Flask(__name__)

# Funktion zum Abrufen der bestehenden Benutzer
def get_users():
    try:
        output = subprocess.check_output("cat /etc/openvpn/easy-rsa/pki/index.txt | grep -E 'V\t'", shell=True)
        users = [line.split('\t')[-1] for line in output.decode('utf-8').split('\n') if line]
        return users
    except Exception as e:
        return str(e)

# Funktion zum Hinzufügen eines neuen Benutzers
def add_user(username):
    try:
        subprocess.check_call(f"cd /etc/openvpn/easy-rsa && ./easyrsa build-client-full {username} nopass", shell=True)
        subprocess.check_call(f"cd /etc/openvpn/easy-rsa && ./easyrsa gen-crl", shell=True)
        return True
    except Exception as e:
        return str(e)

# Funktion zum Abrufen des Serverstatus
def get_server_status():
    try:
        output = subprocess.check_output("systemctl status openvpn@server", shell=True)
        return output.decode('utf-8')
    except Exception as e:
        return str(e)

# Funktion zum Abrufen der Serverauslastung
def get_server_load():
    try:
        output = subprocess.check_output("uptime", shell=True)
        return output.decode('utf-8')
    except Exception as e:
        return str(e)

# Funktion zum Abrufen des Traffics
def get_traffic():
    try:
        output = subprocess.check_output("vnstat -i tun0", shell=True)
        return output.decode('utf-8')
    except Exception as e:
        return str(e)

# Funktion zum Abrufen der Konfiguration
def get_configuration():
    try:
        with open('/etc/openvpn/server.conf', 'r') as file:
            config = file.read()
        return config
    except Exception as e:
        return str(e)

# Funktion zum Herunterladen der Client-Konfiguration
@app.route('/download/<username>', methods=['GET'])
def download(username):
    try:
        path = f"/etc/openvpn/easy-rsa/pki/issued/{username}.crt"
        return send_from_directory('/etc/openvpn/easy-rsa/pki/issued', f"{username}.crt")
    except Exception as e:
        return str(e)

# Funktion zum Löschen eines Benutzers
@app.route('/delete/<username>', methods=['POST'])
def delete_user(username):
    try:
        subprocess.check_call(f"cd /etc/openvpn/easy-rsa && ./easyrsa revoke {username}", shell=True)
        subprocess.check_call(f"cd /etc/openvpn/easy-rsa && ./easyrsa gen-crl", shell=True)
        subprocess.check_call(f"rm /etc/openvpn/easy-rsa/pki/issued/{username}.crt", shell=True)
        subprocess.check_call(f"rm /etc/openvpn/easy-rsa/pki/private/{username}.key", shell=True)
        subprocess.check_call(f"rm /etc/openvpn/easy-rsa/pki/reqs/{username}.req", shell=True)
        return redirect(url_for('index'))
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    users = get_users()
    server_status = get_server_status()
    server_load = get_server_load()
    traffic = get_traffic()
    config = get_configuration()
    return render_template('index.html', users=users, server_status=server_status, server_load=server_load, traffic=traffic, config=config)

@app.route('/add_user', methods=['POST'])
def add_user_route():
    username = request.form['username']
    result = add_user(username)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=900, debug=True)
