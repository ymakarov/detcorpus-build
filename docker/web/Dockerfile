FROM alt
RUN apt-get update
RUN apt-get install --assume-yes git python python3-modules-sqlite3 iconv manatee-open bonito2-open apache2 iproute2 
# setup apache
RUN a2enmod cgi
RUN mkdir -p /var/lock/subsys/http2

# setup apache dir
RUN cp /etc/httpd2/conf/sites-available/bonito2.conf /etc/httpd2/conf/sites-available/detcorpus.conf
RUN sed -i "s/bonito2\?/detcorpus/g" /etc/httpd2/conf/sites-available/detcorpus.conf
RUN mkdir -p /var/www/detcorpus 
RUN a2ensite "detcorpus"
# setup bonito instance
RUN setupbonito /var/www/detcorpus /var/lib/manatee
ENV cgifile="/var/www/detcorpus/run.cgi"
RUN sed -i "s/\[u'susanne'\]/['detcorpus']/" "$cgifile"
RUN sed -i "s/u'susanne'/u'detcorpus'/" "$cgifile"
RUN sed -i "/os.environ\['MANATEE_REGISTRY'\]/s/''/'\/var\/lib\/manatee\/registry'/" "$cgifile"

CMD apachectl -D FOREGROUND
