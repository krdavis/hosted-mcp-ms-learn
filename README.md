# Microsoft Learn Agent (Foundry hosted agent)

A minimal Python hosted agent for Microsoft Foundry that answers questions about Microsoft and Azure technologies using the [Microsoft Learn MCP server](https://learn.microsoft.com/api/mcp).

Built on the Foundry sample [`04-foundry-toolbox`](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents/agent-framework/responses/04-foundry-toolbox) (Microsoft Agent Framework, Responses protocol), trimmed to a single tool.

> **Disclaimer:** This project is provided as is, without warranty of any kind, and is not affiliated with or endorsed by Microsoft. You are responsible for reviewing the code, configuration, security, and costs before deploying it to your own Azure environment.

## How it works

```
user ──► hosted agent container ──► Foundry Toolbox (agent-tools) ──► learn.microsoft.com/api/mcp
              │
              └──► model deployment (created in the Foundry portal)
```

- [src/ms-learn-agent/main.py](src/ms-learn-agent/main.py) creates an Agent Framework `Agent` with a `FoundryChatClient` and a `FoundryToolbox`, then serves it with `ResponsesHostServer` on port 8088.
- [azure.yaml](azure.yaml) declares the Foundry project, the model deployment, a toolbox named `agent-tools` that holds the unauthenticated Microsoft Learn MCP server, and the hosted agent.
- The agent container only calls endpoints inside the Foundry project (the model and the toolbox). The toolbox service makes the outbound call to Microsoft Learn. That keeps the container's egress to one destination if you move the agent onto a private network later.

The Microsoft Learn MCP server exposes tools to search docs, fetch full doc pages, and search code samples.

## Prerequisites

- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) 1.32.0 or later
- The Foundry extension bundle for azd:
  ```bash
  azd ext install microsoft.foundry
  ```
  If you have the older individual extensions installed (for example `azure.ai.agents`), uninstall them first with `azd ext uninstall <id>`.
- Signed in: `azd auth login`
- A Foundry role for the account that runs `azd` (see below)

### Required Foundry role

The account that runs `azd up` needs a Foundry role on the Foundry resource (or project) you deploy to:

| Role | When you need it |
|------|------------------|
| **Foundry User** (formerly Azure AI User) | Minimum to deploy into an existing project. Lets you create the toolbox and the hosted agent, and invoke the agent. |
| **Foundry Project Manager** (recommended) | Everything Foundry User can do, plus assigning the Foundry User role, which `azd up` needs to do for the agent (see below). |

After deploying, `azd up` tries to assign **Foundry User** to the hosted agent's identity so the agent can call the model and the toolbox. That step needs permission to assign roles, which comes with Foundry Project Manager, Foundry Account Owner, User Access Administrator, or Role Based Access Control Administrator. With only Foundry User, that step may fail with a 403, and someone with one of those roles has to assign Foundry User to the agent's identity.

If your account doesn't have Foundry User on the project, `azd` tries to assign it to you, which also needs one of the roles above.

If you let `azd` create a new Foundry resource and project instead of using an existing one, you also need **Contributor** (or Owner) on the subscription or resource group, plus permission to assign roles (Owner or User Access Administrator). See [Azure built-in roles](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles) for details.

## Provision and deploy

Before you start, deploy a model (for example a GPT model) in your Foundry project from the [Foundry portal](https://ai.azure.com), and note its deployment name.

Then, from the project root:

1. Create an azd environment:
   ```bash
   azd env new ms-learn-agent-dev
   ```
2. Point it at your Foundry project. This writes your project endpoint into `azure.yaml`, replacing the placeholder:
   ```bash
   azd ai project add --project-endpoint "https://<account>.services.ai.azure.com/api/projects/<project>" --force
   ```
3. Set the model deployment the agent should use:
   ```bash
   azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME <model-deployment-name>
   ```
4. Provision and deploy the toolbox and the hosted agent:
   ```bash
   azd up
   ```

## Run locally

```bash
azd ai agent run
azd ai agent invoke --local "How do I create an Azure storage account with the CLI?"
```

To run without azd, copy `src/ms-learn-agent/.env.example` to `.env`, fill in the values (the toolbox endpoint is `TOOLBOX_AGENT_TOOLS_MCP_ENDPOINT` from `azd env get-values`), then:

```bash
cd src/ms-learn-agent
python3 -m venv .venv && .venv/bin/pip install uv && .venv/bin/uv sync --active
.venv/bin/python main.py
curl -X POST localhost:8088/responses -H 'Content-Type: application/json' \
  -d '{"input": "How do I create an Azure storage account with the CLI?"}'
```

## Invoke the deployed agent

```bash
azd ai agent invoke "What is Azure Container Apps?"
```

## Credits

Adapted from Microsoft's [foundry-samples](https://github.com/microsoft-foundry/foundry-samples) (MIT License, Copyright (c) 2025 Microsoft Corporation). See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
