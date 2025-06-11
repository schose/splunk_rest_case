# splunk_rest_case

This repo should demonstrate an issue we have with Splunk REST Api. We are trying to validate a clusterbundle on cluster manager and check
if it's needs a restart or not.


## start aws instance as a container host ##


```bash
aws ec2 run-instances --cli-input-yaml file://demohost-aws/demohost.yml --user-data file://demohost-aws/demohost-cloudinit --output yaml