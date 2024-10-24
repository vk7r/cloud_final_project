import globals as g
from cleanup import clear_all
import boto3

ec2 = boto3.client('ec2')

clear_all.clear_all(ec2, g.key_pair_name)
clear_all.delete_security_group(ec2, g.public_security_group_name)
clear_all.delete_security_group(ec2, g.internal_security_group_name)
