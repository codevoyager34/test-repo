Deploying The Server:
Deploy an Ubuntu Server
Point the DNS to the server
SSH into the server
Update the server and install Docker
Copy
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose
sudo systemctl start docker
Set up the docker-compose.yml nano docker-compose.yml
Copy
version: '3.8'  # Using a more recent version for better features
services:
  n8n:
    restart: always
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=verysecurepassword
      - N8N_HOST=horizon-dev.net
      - N8N_PROTOCOL=https
      - N8N_ENCRYPTION_KEY=your-encryption-key-here
      - WEBHOOK_TUNNEL_URL=https://horizon-dev.net
      - WEBHOOK_URL=https://horizon-dev.net
      - N8N_EXTERNAL_URL=https://horizon-dev.net
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres  # Name of the PostgreSQL service in Docker Compose
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=securepassword
      - EXECUTIONS_MODE=regular
      - NODE_FUNCTION_ALLOW_EXTERNAL=nodemailer
      - N8N_PUSH_BACKEND=websocket
      - N8N_PAYLOAD_SIZE_MAX=268435456

    depends_on:
      - postgres  # Ensures PostgreSQL starts before n8n
    volumes:
      - ~/.n8n:/root/.n8n

  postgres:
    restart: always
    image: postgres:latest
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=securepassword
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist PostgreSQL data

volumes:
  postgres_data:  # Define the volume for persisting database data
Build the docker docker-compose up -d
Check that it works
Install NGINX & Certbot apt install nginx certbot
Open port 80 to allow for SSL creation ufw allow 80
Stop NGINX service systemctl stop nginx
Prepare SSL for generation certbot certonly --standalone -d horizon-dev.net
Create DH Params and generate the SSL (The larger the last number is the more secure the server is BUT the longer it takes to generate) openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
Configure NGINX nano /etc/nginx/sites-enabled/horizon-dev.net
Copy
server {
	listen 80;
	listen [::]:80;

	listen 443 ssl http2;
	listen [::]:443 ssl http2;
	ssl_certificate /etc/letsencrypt/live/horizon-dev.net/fullchain.pem; # managed by Certbot
	ssl_certificate_key /etc/letsencrypt/live/horizon-dev.net/privkey.pem; # managed by Certbot
	ssl_trusted_certificate /etc/letsencrypt/live/horizon-dev.net/chain.pem;

	# Improve HTTPS performance with session resumption
	ssl_session_cache shared:SSL:10m;
	ssl_session_timeout 5m;

	# Enable server-side protection against BEAST attacks
	ssl_prefer_server_ciphers on;
	ssl_ciphers ECDH+AESGCM:ECDH+AES256:ECDH+AES128:DH+3DES:!ADH:!AECDH:!MD5;

	# Disable SSLv3
	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

	# Diffie-Hellman parameter for DHE ciphersuites
	# $ sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
	ssl_dhparam /etc/ssl/certs/dhparam.pem;

	# Enable HSTS (https://developer.mozilla.org/en-US/docs/Security/HTTP_Strict_Transport_Security)
	add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";

	# Enable OCSP stapling (http://blog.mozilla.org/security/2013/07/29/ocsp-stapling-in-firefox)
	ssl_stapling on;
	ssl_stapling_verify on;
	resolver 8.8.8.8 8.8.4.4 valid=300s;
	resolver_timeout 5s;

	# Add index.php to the list if you are using PHP
	index index.html index.htm index.nginx-debian.html index.php;

	server_name horizon-dev.net;

  # Increase client body size
  client_max_body_size 256M;

	location = /favicon.ico { access_log off; log_not_found off; }

  # Proxy settings
  location / {
      proxy_pass http://localhost:5678;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_buffering off;
	}

	# deny access to .htaccess files, if Apache's document root
	# concurs with nginx's one
	#
	location ~ /\.ht {
		deny all;
	}

	location ~ /\. {
		access_log off;
		log_not_found off;
		deny all;
	}

	gzip on;
	gzip_disable "msie6";

	gzip_comp_level 6;
	gzip_min_length 1100;
	gzip_buffers 4 32k;
	gzip_proxied any;
	gzip_types
		text/plain
		text/css
		text/js
		text/xml
		text/javascript
		application/javascript
		application/x-javascript
		application/json
		application/xml
		application/rss+xml
		image/svg+xml;

	  access_log off;
	#access_log  /var/log/nginx/horizon-dev.net-access.log;
	error_log   /var/log/nginx/horizon-dev.net-error.log;
}
Restart NGINX systemctl restart nginx
Close port 80 (for security) ufw deny 80 (IF you are using cloudflare skip this step. Instead put force HTTPS in the cloudflare settings)
Allow HTTPS Traffic ufw allow 443
Check the website! 