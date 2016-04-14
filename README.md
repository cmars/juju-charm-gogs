# Juju reactive charm layer for Gogs

## Build

In this directory:

    $ charm build

## Deploy

Gogs needs a PostgreSQL database.

    $ juju deploy cs:~cmars/gogs
    $ juju deploy postgresql
    $ juju add-relation gogs postgresql:db

Browse to port 3000 on the gogs workload.

HTTP reverse proxying is also supported, and recommended for TLS termination.

    $ juju deploy haproxy
    $ juju add-relation gogs haproxy
    $ juju expose haproxy

Then configure the gogs public host name.

    $ juju set-config gogs host=https://git.shlub.com

## License

Copyright 2016 Cmars Technologies, LLC.

The [copyright](copyright) file contains the software license for this charm.

Refer the [Gogs](https://gogs.io/) website for more information on the software
installed by this charm.

## Contact

Cmars Technologies, LLC.

Email: charmed at cmars.tech
IRC: cmars on FreeNode.
