import boto3
import datetime

# Initialize Auto Scaling client
autoscaling = boto3.client("autoscaling")

# Define your Auto Scaling Group name
ASG_NAME = "flask-rds-kajal-asg"

def lambda_handler(event, context):
    # Get the current day of the week
    today = datetime.datetime.utcnow().strftime("%A")

    if today == "Saturday":
        # Scale down to zero
        desired_capacity = 0
    elif today == "Monday":
        # Scale up to one
        desired_capacity = 1
    else:
        return {"message": "No action needed today."}

    # Modify the ASG
    response = autoscaling.update_auto_scaling_group(
        AutoScalingGroupName=ASG_NAME,
        MinSize=0,
        DesiredCapacity=desired_capacity,
        MaxSize=1
    )

    return {
        "message": f"Set ASG '{ASG_NAME}' desired capacity to {desired_capacity}",
        "response": response
    }

