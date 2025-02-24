# **Fast API - Blockhouse Assignment**

## **Overview**
The Fast API project is a real-time order management system developed with FastAPI for the backend and Docker for containerization. It utilizes WebSocket connections to deliver live order status updates and PostgreSQL for data storage. Designed for deployment on an AWS EC2 instance, the system uses Docker and Docker Compose, with an integrated CI/CD pipeline powered by GitHub Actions.

---


## Live Demo
[site](http://3.208.31.87:8000/)

## **Features**
- **Create Orders:** Submit new orders with symbol, price, quantity, and type (buy/sell).
- **Update Orders:** Change order status (e.g., from pending to completed) with a single click.
- **Real-Time Updates:** Get live order status updates using WebSocket connections.
- **RESTful API:** Built with FastAPI for fast, asynchronous request handling.
- **CI/CD Integration:** Automated deployment using GitHub Actions and Docker Hub.
- **Scalable Architecture:** Containerized with Docker for consistent deployment across environments.

---

## **Tech Stack**
- **Backend:** FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **WebSocket:** Real-time updates with FastAPI WebSocket
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions, Docker Hub
- **Cloud Hosting:** AWS EC2 (Ubuntu)

---

## **Prerequisites**
- **Docker & Docker Compose:** Make sure Docker and Docker Compose are installed on your local machine or EC2 instance.
- **AWS EC2 Instance:** Ubuntu is recommended.
- **GitHub Actions:** For automated CI/CD pipeline.
- **Docker Hub Account:** For pushing and pulling container images.

---

## **Getting Started**

### **1. Clone the Repository**
```sh
git clone https://github.com/KunwarBindra/fast-api.git
cd fast-api
```

---

### **2. Environment Variables**
Create a `.env` file in the project root with the following contents:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
POSTGRES_DB=orders
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

### **3. Docker Compose Setup**

**Build and Run:**
```sh
docker-compose up -d --build
```

**Stop and Remove Containers:**
```sh
docker-compose down -v
```

---

### **4. Docker Compose Configuration**
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    volumes:
      - .:/code
    depends_on:
      - db
    networks:
      - trade_network

  db:
    image: postgres:14
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - trade_network

networks:
  trade_network:
    driver: bridge

volumes:
  postgres_data:
```

---

### **5. Accessing the Application**
- **Backend API:** `http://<EC2_PUBLIC_IP>:8000`
- **WebSocket:** `ws://<EC2_PUBLIC_IP>:8000/ws/orders/`

---

### **6. Running Tests**
```sh
pytest tests/
```

---

## **CI/CD Pipeline - GitHub Actions**
This project uses GitHub Actions to automate the build, test, and deployment process.

### **Workflow File: `.github/workflows/deploy.yml`**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Tests
        run: |
          pytest tests/

  build_and_push:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and Push Docker Image
        run: |
          docker build -t kunwarjeetbindra/fast-api-app:latest .
          docker push kunwarjeetbindra/fast-api-app:latest

  deploy:
    runs-on: ubuntu-latest
    needs: build_and_push
    steps:
      - name: Deploy to EC2 via SSH
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          port: ${{ secrets.EC2_PORT }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/${{ secrets.EC2_USER }}/fast-api
            docker-compose down
            docker-compose pull
            docker-compose up -d --build
```

---

## **Secrets Configuration**
Add the following secrets in your GitHub repository:
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token
- `EC2_HOST`: Public IP of your EC2 instance
- `EC2_USER`: `ubuntu` (for Ubuntu)
- `EC2_PORT`: `22`
- `EC2_SSH_KEY`: Private SSH key for EC2 instance access

---

## **Deployment Guide**

### **1. Launch EC2 Instance**
- Use Ubuntu.
- Enable inbound rules for ports:
  - `8000` (API access)
  - `22` (SSH access)

### **2. Install Docker and Docker Compose**

```sh
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### **3. Clone the Repository**

```sh
cd /home/ec2-user
git clone https://github.com/KunwarBindra/fast-api.git
cd fast-api
```

### **4. Start Application**
```sh
docker-compose up -d --build
```

---

## **Troubleshooting**

- **Permission Denied:**
  ```sh
  sudo usermod -a -G docker ec2-user
  newgrp docker
  ```

- **Docker Daemon Not Running:**
  ```sh
  sudo systemctl start docker
  ```

- **Port Not Accessible:**
  - Check EC2 security group rules.

---

## **Contributing**
1. Fork the repository.
2. Create a feature branch:
    ```sh
    git checkout -b feature-name
    ```
3. Commit changes:
    ```sh
    git commit -m "Add new feature"
    ```
4. Push to the branch:
    ```sh
    git push origin feature-name
    ```
5. Open a pull request.

---

## **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## **Contact**
**Kunwarjeet Singh Bindra**  
Email: (bindrak@uci.edu)  
GitHub: (https://github.com/KunwarBindra)

---

## **Acknowledgments**
- Special thanks to the FastAPI and Docker communities for their awesome tools and documentation.
