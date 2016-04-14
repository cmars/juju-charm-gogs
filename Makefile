
ifndef JUJU_REPOSITORY
	$(error JUJU_REPOSITORY is undefined)
endif

CHARM=cs:~cmars/gogs
CHARMS=$(JUJU_REPOSITORY)/trusty/gogs $(JUJU_REPOSITORY)/xenial/gogs
all: $(CHARMS)

$(JUJU_REPOSITORY)/%/gogs:
	charm build -s $*

push:
	charm push $(JUJU_REPOSITORY)/trusty/gogs $(CHARM)

publish:
	charm publish --channel stable $(CHARM)

grant:
	charm grant $(CHARM) --acl read everyone

clean:
	$(RM) -r $(CHARMS)
