# splunk_rest_case

This repo should demonstrate an issue we have with Splunk REST Api. We are trying to validate a clusterbundle on cluster manager and check
if it's needs a restart or not.


## start aws instance as a container host ##


```bash
aws ec2 run-instances --cli-input-yaml file://demohost-aws/demohost.yml --user-data file://demohost-aws/demohost-cloudinit.yml --output yaml
```

- ssh into the instance and clone repo

```bash
git clone https://github.com/schose/splunk_rest_case.git
cd splunk_rest_case
docker network create splunk
docker-compose up -d
```

- wait for the cluster to come up

## steps to reproduce

- copy apps/testapp/indexes.conf to managerapps

```bash
docker cp apps/testapp/default/indexes.conf splunk_rest_case_clm_1:/opt/splunk/etc/manager-apps/_cluster/local/
```

- run validation

```bash
python3 scripts/testvalidation.py localhost:8002
```
There will be no need to restart the cluster

- apply cluster bundle
```bash
docker exec -ti splunk_rest_case_clm_1 sudo -u splunk /opt/splunk/bin/splunk apply cluster-bundle -auth admin:Password01
```

- wait for cluster bundle to be applied

```bash
docker exec -ti splunk_rest_case_clm_1 sudo -u splunk /opt/splunk/bin/splunk show cluster-bundle-status -auth admin:Password01
```

- change homepath of index test1 in apps/testapp/default/indexes.conf - this will enforce a restart of the cluster peers
```bash
sed -i 's|\(homePath.*\)|\11|' apps/testapp/default/indexes.conf
```

- copy apps/testapp/indexes.conf to managerapps

```bash
docker cp apps/testapp/default/indexes.conf splunk_rest_case_clm_1:/opt/splunk/etc/manager-apps/_cluster/local/
```

- run validation

```bash
python3 scripts/testvalidation.py localhost:8002
```

output will be something like this:

```bash
[ec2-user@ip-172-31-17-29 splunk_rest_case]$ python3 scripts/testvalidation.py localhost:8002
Validating bundle...
Bundle checksum: 32C1492DF3A2F93DA1881C71043D9865
Waiting for bundle to be validated...
Attempt 1/6 - Validated checksum: 32C1492DF3A2F93DA1881C71043D9865, Dry run checksum: 32C1492DF3A2F93DA1881C71043D9865, last_check_restart_bundle_result: False
Attempt 2/6 - Validated checksum: 32C1492DF3A2F93DA1881C71043D9865, Dry run checksum: 32C1492DF3A2F93DA1881C71043D9865, last_check_restart_bundle_result: True
Attempt 3/6 - Validated checksum: 32C1492DF3A2F93DA1881C71043D9865, Dry run checksum: 32C1492DF3A2F93DA1881C71043D9865, last_check_restart_bundle_result: True
Attempt 4/6 - Validated checksum: 32C1492DF3A2F93DA1881C71043D9865, Dry run checksum: 32C1492DF3A2F93DA1881C71043D9865, last_check_restart_bundle_result: True
Attempt 5/6 - Validated checksum: 32C1492DF3A2F93DA1881C71043D9865, Dry run checksum: 32C1492DF3A2F93DA1881C71043D9865, last_check_restart_bundle_result: True
Attempt 6/6 - Validated checksum: 32C1492DF3A2F93DA1881C71043D9865, Dry run checksum: 32C1492DF3A2F93DA1881C71043D9865, last_check_restart_bundle_result: True
```