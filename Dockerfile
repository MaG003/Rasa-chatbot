# Sử dụng hình ảnh nginx:latest
FROM nginx:latest

# Sao chép các tệp HTML vào thư mục của Nginx
COPY ./Chatbot-UI /usr/share/nginx/html

# Expose port 80 (port mặc định của Nginx)
EXPOSE 80

# Khởi động Nginx
CMD ["nginx", "-g", "daemon off;"]
