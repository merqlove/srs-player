TAGS := all

install:
	ansible-galaxy install -r provision/requirements.yml --ignore-errors

provision:
	ansible-playbook provision/site.yml --tags=$(TAGS)

deploy:
	ansible-playbook provision/site.yml --tags=player

.PHONY: provision deploy install