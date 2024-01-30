#!/bin/bash
#usage: ./delete-sddc <profile> <region> <org>
docker run -i -w /tmp/scripts/skyler/cmvmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 cmmanageWorkshop.py --profile $1 --region $2 --cmd removeuser --org $3
docker run -i -w /tmp/scripts/skyler/cmvmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 cmmanageWorkshop.py --profile $1 --region $2 --cmd vraccleanup --org $3
#run delete-group again
sleep 60
docker run -i -w /tmp/scripts/skyler/cmvmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 cmmanageWorkshop.py --profile $1 --region $2 --cmd vraccleanup --org $3
docker run -i -w /tmp/scripts/skyler/cmvmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 cmmanageWorkshop.py --profile $1 --region $2 --cmd delete --org $3
