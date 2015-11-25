TAGS := all

provision:
	ansible-playbook -i provision/hosts provision/site.yml --tags=$(TAGS)

deploy:
	ansible-playbook -i provision/hosts provision/production.yml --tags=$(TAGS)

.PHONY: provision deploy