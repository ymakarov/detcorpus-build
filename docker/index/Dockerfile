FROM alt
RUN apt-get update
RUN apt-get install --assume-yes git python python3-modules-sqlite3 iconv unoconv w3m awk manatee-open glibc-locales
COPY mystem-3.1-linux-64bit.tar.gz /home/
RUN tar -xvf /home/mystem-3.1-linux-64bit.tar.gz -C /usr/bin
COPY pandoc-2.7.3-linux.tar.gz /home/
RUN tar xvzf /home/pandoc-2.7.3-linux.tar.gz --strip-components 1 -C /usr/local 
RUN mkdir -p /home/detcorpus-build
COPY Makefile /home/detcorpus-build
COPY remote.mk /home/detcorpus-build
COPY config /home/detcorpus-build/config
COPY scripts /home/detcorpus-build/scripts
COPY make-index /home/make-index
ENV LANG ru_RU.UTF-8  
ENV LANGUAGE ru_RU:en  
ENV LC_ALL ru_RU.UTF-8  
CMD /home/make-index 
