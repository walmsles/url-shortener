import json


import json
import boto3
import os
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.event_handler.exceptions import InternalServerError
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer

app = APIGatewayHttpResolver()
logger = Logger()
tracer = Tracer()

dynamoClient = boto3.resource('dynamodb')
table = dynamoClient.Table(os.environ.get('TABLE', 'TABLE'))

@app.get('/<slug>')
@tracer.capture_method()
def get_url(slug):
    logger.debug(f'slug: {slug}')
    response = table.get_item(Key={"slug": slug})
    item = response.get('Item', None)
    logger.debug(item)
    if item is None:
        return Response(
            status_code = 404,
            content_type='text/html',
            body=f"""
                <html>
                    <head>
                        <meta http-equiv="refresh" content="3;url=https://blog.walmsles.io">
                    </head>
                    <body >
                        <h3>go.walmsl.es</h3>
                        URL Target not found for <b>{slug}</b>
                    </body>
                </html>
            """
        )

    return Response(
        status_code=301, 
        content_type='text/plain', 
        body='',
        headers={"Location": item.get('url')}
    )

@logger.inject_lambda_context()
@tracer.capture_lambda_handler()
def lambda_handler(event, context):
    logger.debug('resolving API')
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.error(str(e))
        return Response(
            status_code = 500,
            content_type='text/html',
            body=f"""
                <html>
                    <head>
                        <meta http-equiv="refresh" content="3;url=https://blog.walmsles.io">
                    </head>
                    <body >
                        <h3>go.walmsl.es</h3>
                        Internal Server Error, lookup aborted
                    </body>
                </html>
            """
        )
