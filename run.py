from src.app import create_app
app, socketio = create_app()



if __name__ == "__main__":
    instance = app.instance_path
    socketio.run(
        app=app, 
        log_output=True, 
        debug=True, 
        certfile=f"{instance}/cert.pem", keyfile=f"{instance}/key.pem")