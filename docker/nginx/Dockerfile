FROM tutum/nginx
RUN mkdir -p /www/static
ADD static/ /www/static
RUN rm /etc/nginx/sites-enabled/default
ADD sites-enabled/ /etc/nginx/sites-enabled
