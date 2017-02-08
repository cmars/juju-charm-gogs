
CHARM=cs:~cmars/gogs
all: builds/gogs

builds/gogs:
	charm build

push:
	charm push builds/gogs $(CHARM)

grant:
	charm grant $(CHARM) --acl read everyone

clean:
	$(RM) -r builds deps
