import logging
import os

import boto3
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer

loglevel = os.environ.get("LOGLEVEL", logging.ERROR)
app = APIGatewayHttpResolver()
logger = Logger(loglevel=loglevel)
tracer = Tracer()

dynamoClient = boto3.resource("dynamodb")
table = dynamoClient.Table(os.environ.get("TABLE", "TABLE"))


def get_env(name: str) -> str:
    value: str = os.environ.get(name, None)
    if not value:
        raise Exception(f"undefined Environment variable [{name}]")

    return value


domain = get_env("DOMAIN")
redirect = get_env("REDIRECT")


def temporary_redirect(url: str) -> Response:
    return Response(
        status_code=302,
        content_type="text/plain",
        body="",
        headers={"Location": url},
    )


def permanent_redirect(url: str) -> Response:
    response: Response = temporary_redirect(url)
    response.status_code = 301

    return response


@app.get("/<slug>")
@tracer.capture_method()
def get_url(slug: str) -> Response:
    logger.debug(f"slug: {slug}")
    response = table.get_item(Key={"slug": slug})
    item = response.get("Item", None)
    logger.debug(item)
    if item is None:
        return temporary_redirect(redirect)

    return permanent_redirect(item.get("url"))


@app.get("/")
def get_domain() -> Response:
    return permanent_redirect(redirect)


@logger.inject_lambda_context()
@tracer.capture_lambda_handler()
def lambda_handler(event, context):
    logger.debug("resolving API")
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.error(str(e))
        return temporary_redirect(redirect)
