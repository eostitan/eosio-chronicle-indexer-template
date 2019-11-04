## EOSIO Chronicle Indexer Template

Employs the open source [EOS Chronicle project](https://github.com/EOSChronicleProject/eos-chronicle) to monitor action traces on EOSIO blockchains, and react with database indexing or other triggered effects. This acts as the simplest template for customised software. It has no error handling.

### To Run

1) Install docker and docker-compose
2) Create a `chronicle-receiver/config/config.ini` file like the example, and modify as with the host and port for the state history node you wish to connect to
3) `docker-compose up -d`

### To monitor consumer log file
`tail -f chronicle-consumer/debug.log`

...or for just errors...

`tail -f chronicle-consumer/debug.log | grep 'ERROR'`

