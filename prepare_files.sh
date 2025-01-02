#!/bin/bash
# ==================== Create directories ====================
if [ ! -d user_data/_outputs/ ]
  then
    mkdir user_data/_outputs/
fi

# ==================== Main files - accounts.csv and settings.json ====================
if [ ! -s user_data/_inputs/csv/accounts.csv ]
  then :
    echo "Creating accounts.csv file in 'user_data/_inputs/csv/'"
    touch user_data/_inputs/csv/accounts.csv && echo "account_id,account_address,private_key,transfer_address,proxy" >> user_data/_inputs/csv/accounts.csv
fi

if [ ! -s user_data/_inputs/envs/.env ]
  then :
    echo "Creating .env file in 'user_data/_inputs/envs/'"
    cp user_data/_inputs/envs/example.env user_data/_inputs/envs/.env
fi

if [ ! -s user_data/_inputs/json/settings.json ]
  then :
    echo "Creating settings.json file in 'user_data/_inputs/json/'"
    cp user_data/_inputs/json/settings.example.json user_data/_inputs/json/settings.json
fi

if [ ! -s user_data/_inputs/settings/_global.py ]
  then :
    echo "Creating _global.py file in 'user_data/_inputs/settings/'"
    cp user_data/_inputs/settings/_global.example.py user_data/_inputs/settings/_global.py
fi