# Server
from app.main import create_app

# Setting
import sys
import uvicorn
from typing import Optional
import os

def run_server(host: Optional[str] = None, port: Optional[int] = None, build:str = "dev") -> None:

    host = host or "0.0.0.0"
    port = port or 8088
    app = create_app()

    print("host:",host,"port:",port);
    uvicorn.run(app, host=host, port=port)

def main():
    input_ = sys.argv
    
    prompt = "_".join(input_[1:])
    
    #runserver
    if prompt == "runserver": run_server()

    #other
    else: raise Exception('Not Command')


if __name__=="__main__":
    main()