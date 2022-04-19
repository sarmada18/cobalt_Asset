import boto3
import json
import traceback

sqs_message = {'function_name':"",'log_group_name':"",'log_stream_name':"",'resources_deleted':[],"error":"no"}

def lambda_handler(event, context):

    global sqs_message

    #populating values to sqs_message keys
    sqs_message['function_name'] = context.function_name
    sqs_message['log_group_name'] = context.log_group_name
    sqs_message['log_stream_name'] = context.log_stream_name

    try:

    #describing all regions of AWS, so that code can be executed for every region
        ec2 = boto3.client('ec2')
        response = ec2.describe_regions()
        regions = response['Regions']

    #Executing for every region
        for i in range(0, len(regions)):
            region_name = regions[i]['RegionName']
            get_launch_configurations(region_name)

    except:
        sqs_message["error"] = "yes"
        print("Script Execution error, view details below")
        print(traceback.format_exc())

    #send a message to sqs queue after every execution
    finally:
        send_to_sqs()

#fetches the launch configurations available in that region
def get_launch_configurations(region):
    client = boto3.client('autoscaling', region_name=region)
    response = client.describe_launch_configurations()
    for i in range(0, len(response['LaunchConfigurations'])):
        Config_name = response['LaunchConfigurations'][i]['LaunchConfigurationName']
        print(Config_name)
        delete_launch_configurations(Config_name, region)

#deletes the launch configuration in that region
def delete_launch_configurations(Config_name,region):
    client = boto3.client('autoscaling', region_name=region)
    sqs_message['resources_deleted'].append([Config_name, region])
    client.delete_launch_configuration(
        LaunchConfigurationName=Config_name
    )

#sends message to the specified queue(Modify the SQS queue URL accordingly)
def send_to_sqs():
    sqs_queue_url = "https://sqs.ap-south-1.amazonaws.com/462352741814/sqs-queue-auto-scripts"
    global sqs_message
    print(sqs_message)
    sqs_client = boto3.client('sqs')
    json_message = json.dumps(sqs_message, indent=4)
    sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json_message)



























