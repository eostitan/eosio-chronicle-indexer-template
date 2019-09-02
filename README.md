## EOSIO Chronicle Indexer

Will employ the open source Chronicle project to collect and organise data from EOSIO blockchains.

### To Run

1) Install docker and docker-compose
2) Create a `cronicle-receiver/config/config.ini` file like the example, and modify as with the host and port for the state history node you wish to connect to
3) `docker-compose up -d`

### To monitor consumer log file
`tail -f chronicle-consumer/debug.log`

...or for just errors...

`tail -f python_aggregator/debug.log | grep 'ERROR'`

