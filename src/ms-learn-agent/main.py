# Portions copyright (c) Microsoft Corporation. Adapted from the foundry-samples
# 04-foundry-toolbox sample (MIT License). See THIRD-PARTY-NOTICES.md.

import asyncio
import logging
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import FoundryToolbox, ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load local .env values without overriding variables Foundry injects at runtime
load_dotenv(override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("ms-learn-agent")

INSTRUCTIONS = """\
You are a Microsoft technology assistant. Answer questions about Microsoft and
Azure products, services, SDKs, and APIs.

- Always ground your answers in official documentation by using the Microsoft
  Learn tools: search the docs first, fetch a full page when the search excerpts
  are not enough, and search code samples when the user asks for code.
- Keep answers concise and practical.
- Cite the Microsoft Learn URLs you used at the end of each answer.
- If the documentation does not cover the question, say so rather than guessing.
"""


async def main():
    credential = DefaultAzureCredential()

    # FoundryToolbox resolves the toolbox endpoint from TOOLBOX_ENDPOINT (or
    # FOUNDRY_PROJECT_ENDPOINT + TOOLBOX_NAME) and authenticates every request
    # with the credential. The toolbox exposes the Microsoft Learn MCP server.
    toolbox = FoundryToolbox(credential)

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=credential,
    )

    agent = Agent(
        client=client,
        name="ms-learn-agent",
        instructions=INSTRUCTIONS,
        tools=toolbox,
        # History is managed by the hosting infrastructure, so the model
        # service doesn't need to store it.
        default_options={"store": False},
    )

    logger.info("Starting ms-learn-agent on port %s", os.environ.get("PORT", "8088"))
    server = ResponsesHostServer(agent)
    await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
