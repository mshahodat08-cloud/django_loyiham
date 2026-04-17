#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M)

mkdir -p /var/www/blog/backups

pg_dump -U blog_user blog_db > /var/www/blog/backups/db_$DATE.sql

find /var/www/blog/backups -name "*.sql" -mtime +7 -delete
