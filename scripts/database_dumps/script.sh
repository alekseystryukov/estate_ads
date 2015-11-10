#! /bin/bash

TIMESTAMP=$(date +"%F")
BACKUP_DIR="$TIMESTAMP"

MYSQL_HOST="159.224.7.74"
MYSQL_USER="estate_ads"
MYSQL=/usr/bin/mysql
MYSQL_PASSWORD="dopler"
DATABASE="estate_ads"
MYSQLDUMP=/usr/bin/mysqldump


mkdir -p "$BACKUP_DIR"

mysqldump --force --opt -h$MYSQL_HOST --user=$MYSQL_USER -p$MYSQL_PASSWORD --databases $DATABASE | gzip > "$BACKUP_DIR/$DATABASE.gz"


#databases=`$MYSQL --user=$MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW DATABASES;" | grep -Ev "(Database|information_schema|performance_schema)"`
#for db in $databases; do
  #$MYSQLDUMP --force --opt --user=$MYSQL_USER -p$MYSQL_PASSWORD --databases $db | gzip > "$BACKUP_DIR/$db.gz"
#done