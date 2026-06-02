FROM nginx:1.25-alpine

# Remove default configuration template
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom configuration explicitly over the default target name
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]