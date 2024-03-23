# Use an official nginx image as a base
FROM nginx:alpine

# Copy the HTML file into the image
COPY Testfile.html /usr/share/nginx/html/Testfile.html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
