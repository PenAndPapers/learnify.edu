FROM nginx:1.25-alpine

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

COPY infra/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]