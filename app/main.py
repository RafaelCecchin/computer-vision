import subprocess
import signal

def main():
    processes = []
    try:
        flask_process = subprocess.Popen(["python", "http/flask_server.py"])
        websocket_process = subprocess.Popen(["python", "http/websocket_server.py"])
        processes.extend([flask_process, websocket_process])
        
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("Interrompido. Encerrando servidores...")
        for process in processes:
            process.terminate()
    finally:
        for process in processes:
            process.wait()

if __name__ == '__main__':
    main()
