from flask import current_app, has_app_context

def get_config(key:str):     
    if has_app_context() and not current_app.config.get('TESTING',True):
            value = current_app.config.get(key)
    else:
        # TODO: Change this later
        value = "TESTING"
    assert value is not None
    return value