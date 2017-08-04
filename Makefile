
CHARM=cs:~cmars/gogs
BDIST_VERSION=0.9.141

all: builds/gogs

builds/gogs: bdist/gogs.tar.gz
	charm build

bdist/gogs.tar.gz:
	-mkdir -p $(shell dirname $@)
	wget -O $@ https://dl.gogs.io/gogs_v$(BDIST_VERSION)_linux_amd64.tar.gz

push: builds/gogs bdist/gogs.tar.gz
	charm push builds/gogs $(CHARM) --resource bdist=bdist/gogs.tar.gz

grant:
	charm grant $(CHARM) --acl read everyone

clean:
	$(RM) -r builds deps
