# SETUP PATHS
ROOT=..
SRC=$(ROOT)/detcorpus
vpath %.txt $(SRC)
vpath %.fb2 $(SRC)
vpath %.html $(SRC)
vpath %.csv $(SRC)
#
# SETUP CREDENTIALS
HOST=detcorpus
# CHROOTS
TESTING=testing
PRODUCTION=production
ROLLBACK=rollback
TESTPORT=8098
PRODPORT=8099
BUILT=built
RSYNC=rsync -avP --stats -e ssh
#
## corpora
corpbasename := detcorpus
corpsite := detcorpus
corpora := detcorpus
corpora-vert := $(addsuffix .vert, $(corpora))
compiled := $(patsubst %,export/data/%/word.lex,$(corpora))
## Remote corpus installation data
corpsite-detcorpus := detcorpus
#
#
## SETTINGS
SHELL := /bin/bash
.PRECIOUS: %.txt
.PHONY: unoconv-listener
## UTILS
gitsrc=git --git-dir=$(SRC)/.git/

## HARDCODED FILELIST TWEAKS
duplicatesrc := $(shell $(gitsrc) ls-files dups)
skipfiles := emolemmas.txt emowords.txt $(shell $(gitsrc) ls-files depot) 
## STANDARD SOURCE FILELISTS
gitfiles := $(shell $(gitsrc) ls-files)
srcfiles := $(filter-out $(duplicatesrc) $(skipfiles), $(gitfiles))
txtfiles := $(filter %.txt, $(srcfiles))
srchtmlfiles := $(filter %.html, $(srcfiles))
srctxtfiles := $(filter-out $(fb2files:.fb2=.txt) $(srchtmlfiles:.html=.txt), $(txtfiles))
srcfb2files := $(filter %.fb2, $(srcfiles))
vertfiles := $(srcfb2files:.fb2=.vert) $(srctxtfiles:.txt=.vert) $(srchtmlfiles:.html=.vert)

help:
	 @echo 'Makefile for building detcorpus                                           '
	 @echo '                                                                          '
	 @echo 'Corpus texts source files are expected to be found at: $(SRC)             '
	 @echo '                                                                          '
	 @echo '                                                                          '
	 @echo 'Dependencies: git, python, unoconv, w3m, awk, mystem, daba(TBDeleted)     '
	 @echo '              manatee-open                                                '
	 @echo '                                                                          '
	 @echo 'Usage:                                                                    '
	 @echo '   make convert	    convert all sources (fb2, html) into txt             '
	 @echo '   make compile      prepare NoSke indexes for all corpora for upload     '
	 @echo '                                                                          '

## remote operation scripts
include remote.mk

print-%:
	$(info $*=$($*))

%.txt: %.fb2 | unoconv-listener
	test -d $(@D) || mkdir -p $(@D)
	unoconv -n -f txt -e encoding=utf8 -o $@ $<

%.txt: %.html
	test -d $(@D) || mkdir -p $(@D)
	w3m -dump $< > $@

%.vert: %.html
	test -d $(@D) || mkdir -p $(@D)
	w3m -dump $< | mystem -n -d -i -g -c -s --format xml $< | sed 's/[^[:print:]]//g' | python mystem2vert.py $@ > $@
	metaprint -a $< | fgrep -v _auto | sed 's/^\([^:]\+\):/\1_/' | awk -F"\t" 'length($$2) {printf "%s=\"%s\" ", $$1, $$2}' > $*.meta
	sed -i "1 s\(<doc id=[^ >]\+\).*$$\1 $$(cat $*.meta)>" $@

%.vert: %.txt
	test -d $(@D) || mkdir -p $(@D)
	mystem -n -d -i -g -c -s --format xml $< | sed 's/[^[:print:]]//g' | python mystem2vert.py $@ > $@

detcorpus.vert: $(vertfiles)
	cat $(SRC)/genres.csv | tr ',' ' ' | while read d id genre ; do test -f $$d/$${id%.*}.vert && sed -i "1s/>/ subcorpus=\"$$genre\">/" $$d/$${id%.*}.vert; done
	rm -f $@
	echo "$(sort $^)" | tr ' ' '\n' | while read f ; do cat "$$f" >> $@ ; done

export/data/%/word.lex: config/% %.vert
	rm -rf export/data/$*
	rm -f export/registry/$*
	mkdir -p $(@D)
	mkdir -p export/registry
	mkdir -p export/vert
	encodevert -c ./$< -p $(@D) $*.vert
	cp $< export/registry
ifneq ("$(wildcard config/$*.subcorpora)","")
	echo "no subcorpora defined for $*:: $(wildcard config/$*.subcorpora)"
else
	mksubc ./export/registry/$* export/data/$*/subcorp config/$*.subcorpora
endif
	sed -i 's,./export,/var/lib/manatee/,' export/registry/$*

export/detcorpus.tar.xz: $(compiled)
	rm -f $@
	bash -c "pushd export ; tar cJvf detcorpus.tar.xz --mode='a+r' * ; popd"

unoconv-listener:
	unoconv --listener &
	sleep 10

compile: $(compiled)

convert: $(vertfiles:.vert=.txt) 
