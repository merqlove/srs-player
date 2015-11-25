# Player
Simple audio streaming demo with HTML5/FLASH player, based on [SRS](http://ossrs.net).

Requirements:
- Python 2.7+
- Ansible
- Vagrant

## Production:

    # Provision
    $ make provision

    # Deploy
    $ make deploy

    # Provision with tags
    $ TAGS=provision make deploy

## Development:

    # Setup server
    $ vagrant up

    # Provision
    $ vagrant provision

    # Provision with tags
    $ TAGS=player vagrant provision
