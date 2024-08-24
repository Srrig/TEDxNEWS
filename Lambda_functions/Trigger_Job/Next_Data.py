# Set up logging
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import Boto 3 for AWS Glue
client = boto3.client('glue')

# Variables for the job:
glueJobName = "watch_next"  # Nome del job Glue da avviare

# Define Lambda function
def lambda_handler(event, context):
    try:
        # Avvia il job Glue
        response = client.start_job_run(JobName=glueJobName)
        logger.info('## STARTED GLUE JOB: ' + glueJobName)
        logger.info('## GLUE JOB RUN ID: ' + response['JobRunId'])

        # Restituisci una risposta positiva
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Glue job started successfully',
                'JobRunId': response['JobRunId']
            })
        }
    except Exception as e:
        logger.error(f'## Failed to start Glue job: {glueJobName}. Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Failed to start Glue job: {glueJobName}. Error: {str(e)}'
            })
        }
