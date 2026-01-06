FROM nginx:alpine

# Copy frontend files to nginx html directory
COPY index.html style.css script.js /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Nginx will start automatically

