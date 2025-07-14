sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update && sudo apt install python3.12 python3.12-venv python3.12-dev

poetry env use python3.12

potery install 

echo "SECRET_KEY=$(openssl rand -hex 32)" > .env