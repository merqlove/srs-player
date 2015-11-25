# Player
Simple audio streaming demo with HTML5/FLASH player, based on SRS.

Requirements:
- Python 2.7+
- Ansible
- Vagrant

## Production:

    # Provision
    $ make provision

    # Deploy
    $ make deploy

    # Deploy or provision with tags
    $ TAGS=player make deploy

## Development:

    # Setup server
    $ vagrant up

    # Provision
    $ vagrant provision

    # Provision with tags
    $ TAGS=player vagrant provision
