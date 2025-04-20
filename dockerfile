# Use an official web server image
FROM nginx:alpine

# Copy your website files to the Nginx HTML folder
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80
