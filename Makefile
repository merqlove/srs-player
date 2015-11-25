TAGS := all

provision:
	ansible-playbook -i provision/hosts provision/site.yml --tags=$(TAGS)

deploy:
	ansible-playbook -i provision/hosts provision/site.yml --tags=player

.PHONY: provision deploy