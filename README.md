## To set SSH connection on Windows you need to run next commands in command line:
```
cd [path_to_key_files]
mkdir %HOMEDRIVE%%HOMEPATH%\.ssh 
type ssh_key.pub >> %HOMEDRIVE%%HOMEPATH%\.ssh\id_rsa.pub
type ssh_key >> %HOMEDRIVE%%HOMEPATH%\.ssh\id_rsa
```
## Enter the server with ssh command:
```
ssh root@smafed.com
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
##### To edit ```docker-compose-prod.yml``` file you can use ubuntu nano editor in the next way:
```
nano docker-compose-prod.yml
```
### After any changing in ```docker-compose-prod.yml``` or in the scripts you MUST run multi-container application with rebuilding:
```
docker-compose -f docker-compose-prod.yml up -d --build
```
## To update or replace IKB database you need to do the following commands
##### Stop multi-container application and run only mongodb
```
docker-compose -f docker-compose-prod.yml down
docker run -p 27017:27017 --name mongo -v /root/event-detection-app/data/mongodb/db:/data/db -d mongo
```
##### Open another command line window and copy the new database file to the server
```
scp /path/to/new/IKB/on/your/computer/<NEW_IKB_filename> root@smafed.com:/root/event-detection-app
```
##### Return to the previous command line window when download will be completed and enter the Mongo shell inside the docker container:
```
docker cp <NEW_IKB_filename> mongo:<NEW_IKB_filename>
docker exec -it mongo bash
mongo
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
mongoimport --db event_detection_db --collection IKB <NEW_IKB_filename> --jsonArray
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
mongoimport --db event_detection_db --collection IKB <NEW_IKB filename>
exit
```
#### In both cases in the end you have to run multi-container application again:
```
docker-compose -f docker-compose-prod.yml up -d
```