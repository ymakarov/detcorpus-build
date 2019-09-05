FROM alt
RUN apt-get update
RUN apt-get install --assume-yes git python python3-modules-sqlite3 iconv manatee-open bonito2-open apache2 iproute2
RUN mkdir /var/lib/manatee
# setup apache
#RUN a2disport http
#WORKDIR /etc/httpd2/conf/
#RUN cp ports-available/http-localhost-8088.conf ports-available/80.conf
#RUN sed -i "s/8088/80/g" ports-available/80.conf
#RUN sed -i "/^Listen/s/localhost/127.0.0.1/" ports-available/80.conf
#RUN a2enport "80"
RUN a2enmod cgi

#setup corpus
#COPY detcorpus.tar.xz /home/detcorpus.tar.xz
#RUN tar --no-same-permissions --no-same-owner -xJvf /home/detcorpus.tar.xz --directory /var/lib/manatee
#RUN export MANATEE_REGISTRY=/var/lib/manatee/registry && mksizes detcorpus 
#COPY detcorpus.vert /var/lib/manatee/vert
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
RUN mkdir -p /var/lock/subsys/http2
