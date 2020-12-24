# Enter the server with ssh command:
```
# (Reference: cd ~/Downloads)
ssh -i path/to/file/with/private/key root@smafed.com  
```
## Go to the folder with application:
```
cd event-detection-app
```
## To run multi-container application with configuration described in `docker-compose-prod.yml` file:
```
cd event-detection-app
docker-compose -f docker-compose-prod.yml up -d 
```
## You can configure ```docker-compose-prod.yml```:
##### You have to set your access tokens of twitter developer account
      - ACCESS_TOKEN
      - ACCESS_SECRET
      - CONSUMER_KEY
      - CONSUMER_SECRET
##### You have to set url for [sent2vec model](https://github.com/epfml/sent2vec#downloading-sent2vec-pre-trained-models) and [spellchecking model](https://github.com/bakwc/JamSpell#download-models) downloading
      - URL_FOR_SENTTOVEC_MODEL
      - URL_FOR_SPELLCHECKER_MODEL
##### To set number of tokens in tweet and parameters of clustering algorithm
      - NUM_OF_TOKENS
      - SHR_MIN
      - SHR_THRESHOLD
      - HISTOGRAM_RATIO_COEFFICIENT
##### To edit ```docker-compose-prod.yml``` file you can use ubuntu nano editor in the next way:
```
docker-compose -f docker-compose-prod.yml down
nano docker-compose-prod.yml
```
### After any changing in ```docker-compose-prod.yml``` or in the scripts you MUST run multi-container application with rebuilding:
```
docker-compose -f docker-compose-prod.yml up -d --build
docker system prune -a
```
## To update or replace IKB database you need to do the following commands
##### Stop multi-container application and run only mongodb
```
docker-compose -f docker-compose-prod.yml down
docker run -p 27017:27017 --name mongo -v /root/event-detection-app/data/mongodb/db:/data/db -d mongo --auth
```
##### Open another command line window and copy the new database file to the server
```
scp -i path/to/file/with/private/key /path/to/new/IKB/on/your/computer/<NEW_IKB_filename> root@smafed.com:/root/event-detection-app
```
##### Return to the previous command line window when download will be completed and enter the Mongo shell inside the docker container:
```
docker cp <NEW_IKB_filename> mongo:<NEW_IKB_filename>
docker exec -it mongo bash
mongo --username admin --password ZgtnQKNUeSVhBLW3LBfU --authenticationDatabase admin
```
#### Then you can choose how to delete the database.
##### 1. Fully remove old database(all information about old clusters, tweets and slang words):
```
use event_detection_db
db.IKB.remove({})
db.tweets_input.remove({})
db.tweets_processed.remove({})
db.cluster.remove({})
db.used_slang.remove({})
exit
```
##### Import a new one:
```
mongoimport --db event_detection_db --collection IKB <NEW_IKB_filename> --username admin --password ZgtnQKNUeSVhBLW3LBfU --authenticationDatabase admin
exit
```
##### Clean up old cluster`s staff:
```
sudo rm -rf /root/event-detection-app/data_smafed/cluster
```
##### 2.Remove only IKB:
```
use event_detection_db
db.IKB.remove({})
exit
```
##### Import a new one:
```
mongoimport --db event_detection_db --collection IKB <NEW_IKB_filename> --username admin --password ZgtnQKNUeSVhBLW3LBfU --authenticationDatabase admin
exit
```
#### In both cases in the end you have to stop mongodb and run multi-container application:
```
docker stop mongo
docker rm mongo
docker-compose -f docker-compose-prod.yml up -d
```
## To delete all clusters you need to do the following commands
##### Stop multi-container application and run only mongodb
```
docker-compose -f docker-compose-prod.yml down
docker run -p 27017:27017 --name mongo -v /root/event-detection-app/data/mongodb/db:/data/db -d mongo --auth
```
##### Enter the Mongo shell inside the docker container:
```
docker exec -it mongo bash
mongo --username admin --password ZgtnQKNUeSVhBLW3LBfU --authenticationDatabase admin
```
##### Fully remove old database(all information about old clusters, tweets and slang words):
```
use event_detection_db
db.tweets_input.remove({})
db.tweets_processed.remove({})
db.cluster.remove({})
db.used_slang.remove({})
exit
exit
```
##### Clean up old cluster`s staff:
```
sudo rm -rf /root/event-detection-app/data_smafed/cluster
```
#### In the end you have to stop mongodb and run multi-container application:
```
docker stop mongo
docker rm mongo
docker-compose -f docker-compose-prod.yml up -d
```
# Additional. Run application from zero on the new server.
### For running application from zero on the new server you have to follow next steps.
##### Note!!! SSH-client have to be installed on your system.
Connect to the server via ssh and create app folder, look at full path to this folder and remember it.
```
ssh -i <path to the private key> <server user>@<server>
mkdir event-detection-app
cd event-detection-app
pwd
exit
```
Copy IKB.json file to the server.
```
scp -i <path to the private key> <path to the IKB.json> user>@<server>:<path to the app folder on the server>
```
Again connect to the server via ssh.
```
ssh -i <path to the private key> <server user>@<server>
cd event-detection-app
```
Install git, crontab and docker if it isn't installed.
```
apt-get update && apt-get install -y git docker cron
```
Run mongodb container and copy IKB to this container.
```
docker run -p 27017:27017 --name mongo -v <path to the app folder on the server>/data/mongodb/db:/data/db -d mongo
docker cp <IKB file> mongo:<IKB file>
```
Import data.
```
docker exec -it mongo bash
mongoimport --db event_detection_db --collection IKB <IKB file>
```
Then create user for authentication.
```
mongo
use admin
db.createUser({user: "admin", pwd: "ZgtnQKNUeSVhBLW3LBfU", roles: ["readWriteAnyDatabase"]});
exit
exit
```
Stop and remove mongodb container.
```
docker stop mongo
docker rm mongo
```
Create file `cron_job.sh` with following text. You can create it with command `nano cron_job.sh`
```
#!/bin/bash
docker-compose -f <path to the app folder on the server>/docker-compose-prod.yml down
docker-compose -f <path to the app folder on the server>/docker-compose-prod.yml up -d
```
Then make this file runnable with command `chmod a+x cron_job.sh`

Next step will be creating cron job for restarting system every day for deleting cached logs.

With writing `crontab -e` window for crontab jobs will be opening. Paste following line in the end of the file then save changes and exit with `Ctrl + S` and `Ctrl + X`.
```
0 0 * * * sudo <path to the app folder on the server>/cron_job.sh
```
Go to app folder and clone your app from repository.
```
git clone <link to you repository>
```
After cloning change credentials of Twitter API. Set following access tokens of twitter developer account with `nano docker-compose-prod.yml`. Save changes and exit with `Ctrl + S` and `Ctrl + X`.
```
- ACCESS_TOKEN
- ACCESS_SECRET
- CONSUMER_KEY
- CONSUMER_SECRET
```
Build and run application.
```
docker-compose -f docker-compose-prod.yml up -d
```
