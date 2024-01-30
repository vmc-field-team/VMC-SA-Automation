#!/bin/bash
#usage: ./create-sddc <profile> <region> <org> <password> <provider>
docker run -i -w /tmp/scripts/skyler/vmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 manageWorkshop.py --profile $1 --region $2 --cmd create --org $3 --pwd $4 --provider $5
docker run -i -w /tmp/scripts/skyler/vmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 manageWorkshop.py --profile $1 --region $2 --cmd create-route --org $3
docker run -i -w /tmp/scripts/skyler/vmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 manageWorkshop.py --profile $1 --region $2 --cmd adduser --org $3
