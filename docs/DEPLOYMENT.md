# Production Deployment Guide
## AI-Enabled Fleet Digital Twin for Predictive Vehicle Maintenance

This document provides instructions for deploying the Fleet Digital Twin application to enterprise Linux servers, Docker environments, and cloud platforms.

---

## 🏛️ Production Architecture Overview

In a production environment, the Flask application should not run using the built-in development server (`run.py`). Instead, it is served behind a production WSGI HTTP server (such as **Gunicorn** or **Waitress**) reverse-proxied by **Nginx** for SSL termination, static asset caching, and security headers.

```text
[ Internet / Fleet Telemetry Streams ]
                 │
                 ▼
       [ Nginx Reverse Proxy ]
     (Port 80/443, SSL/TLS, Caching)
                 │
                 ▼
      [ Gunicorn WSGI Workers ]
       (Unix Socket / Port 5000)
                 │
                 ▼
     [ Flask Application Factory ]
   ├── REST Ingestion Gateways (/api)
   ├── Digital Twin Simulation Engine
   ├── Scikit-learn Classifier (model.pkl)
   └── SQLite ACID Database (fleet_data.db)
```

---

## 🐳 1. Docker Deployment

### Step 1: Review Environment Variables
Copy `.env.example` to `.env` and configure production secrets:
```bash
cp .env.example .env
```
Ensure `SECRET_KEY` is set to a secure, randomly generated string:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 2: Build and Run
```bash
docker-compose up --build -d
```

### Step 3: Monitor Container Health and Logs
```bash
# Check container status
docker-compose ps

# Follow application logs
docker-compose logs -f
```

---

## 🐧 2. Linux VPS (Ubuntu 22.04 LTS) with Systemd & Nginx

### Step 1: Install System Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git curl
```

### Step 2: Clone Code & Configure Virtual Environment
```bash
cd /var/www
sudo git clone https://github.com/your-username/ai-fleet-digital-twin.git fleet-twin
cd fleet-twin

sudo python3 -m venv venv
sudo ./venv/bin/pip install --upgrade pip
sudo ./venv/bin/pip install -r requirements.txt
sudo ./venv/bin/pip install gunicorn

# Initialize Database & seed initial fleet
sudo ./venv/bin/python database/init_db.py

# Create system user & assign permissions
sudo useradd -r -s /bin/false fleetapp
sudo chown -R fleetapp:fleetapp /var/www/fleet-twin
```

---

### Step 3: Configure Systemd Service
Create the systemd service file:
```bash
sudo nano /etc/systemd/system/fleet-twin.service
```
Insert the following configuration:
```ini
[Unit]
Description=Gunicorn instance serving Fleet Digital Twin
After=network.target

[Service]
User=fleetapp
Group=fleetapp
WorkingDirectory=/var/www/fleet-twin
Environment="PATH=/var/www/fleet-twin/venv/bin"
Environment="FLASK_CONFIG=production"
Environment="SECRET_KEY=your-production-secret-key-here"
ExecStart=/var/www/fleet-twin/venv/bin/gunicorn --workers 4 --threads 2 --bind 127.0.0.1:5000 wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fleet-twin
sudo systemctl start fleet-twin
sudo systemctl status fleet-twin
```

---

### Step 4: Configure Nginx as Reverse Proxy
Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/fleet-twin
```
Add the server block:
```nginx
server {
    listen 80;
    server_name fleet-twin.yourdomain.com; # Replace with your IP or domain

    # Static file serving optimization
    location /static/ {
        alias /var/www/fleet-twin/app/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Proxy all dynamic requests to Gunicorn WSGI
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable the site and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/fleet-twin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 5: Enable SSL / HTTPS (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d fleet-twin.yourdomain.com
```

---

## ☁️ 3. Cloud PaaS Deployment (Render / Railway / Heroku)

### Render / Railway:
1. Connect your GitHub repository.
2. Set Build Command:
   ```bash
   pip install -r requirements.txt && pip install gunicorn && python database/init_db.py
   ```
3. Set Start Command:
   ```bash
   gunicorn wsgi:application --bind 0.0.0.0:$PORT
   ```
4. Set Environment Variables:
   - `FLASK_CONFIG`: `production`
   - `SECRET_KEY`: `<Generate a random 32-character string>`

---

## 🛡️ Production Security Checklist

- [ ] Changed default `SECRET_KEY` from template values.
- [ ] Debug mode is disabled (`FLASK_DEBUG=False`).
- [ ] Database file permissions restricted (`chmod 660 database/fleet_data.db`).
- [ ] Changed administrator default password (`admin123`) in `app/routes/views.py`.
- [ ] SSL/TLS certificate configured for all traffic.
- [ ] Monitored log file rotation (`logs/fleet_twin.log`).
