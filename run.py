import os
import sys
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    from app import app
    local_ip = get_local_ip()
    
    print('=' * 65)
    print('       BUSINESS EXPENSE TRACKER - Network Server Mode        ')
    print('=' * 65)
    print('  * On this computer : http://localhost:5000')
    print(f'  * On other devices : http://{local_ip}:5000')
    print('=' * 65)
    print('  (Ensure other devices are connected to the same Wi-Fi network)')
    print('  Press CTRL+C to stop the server.')
    print('=' * 65)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
