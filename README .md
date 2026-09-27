# Safe Shopping Agent

A small Python agent for Topic 07: Simple Safe Agent. It uses a local Ollama model to select shopping tools, while Python application code controls whether those tools may run.

## 1. Project Overview

The agent helps a user search for products and check their stock. It also has an administrator-only tool that deletes a product from the practice data.

The model requests tools; the application validates and executes them. Tool results are sent back to the model so it can choose another action or finish the request.

The project uses:

- Python and PyCharm on Windows.
- Ollama with `qwen3:4b` running locally.
- The `ollama` Python package to communicate with the model.
- The `jsonschema` package to validate tool arguments.

The product data starts with:

| ID | Product | Stock |
| --- | --- | --- |
| 1 | Dell Laptop | 0 |
| 2 | Lenovo Laptop | 5 |
| 3 | Wireless Mouse | 12 |

This is an in-memory demonstration. Changes last for the current Python process; restarting the program restores the original data.

### Project files

| File | Purpose |
| --- | --- |
| `main.py` | Interactive terminal interface and application-selected role. |
| `agent.py` | Model communication, agent loop, execution limits, and stock evidence handling. |
| `tools.py` | Product data and the three tool implementations. |
| `schemas.py` | Tool descriptions and JSON Schemas for their inputs. |
| `harness.py` | Tool registry, permission checks, validation, and controlled execution. |
| `requirements.txt` | Python dependencies. |
| `test_log.md` | Recorded test commands, outputs, and coverage notes. |
| `README.md` | Project explanation and setup instructions. |

## 2. Available Tools

| Tool | Input | Result | Allowed roles |
| --- | --- | --- | --- |
| `search_products` | `keyword`: string, 1–100 characters | Matching product IDs and names. | Customer, admin |
| `check_stock` | `product_id`: integer, at least 1 | Product ID, name, stock quantity, and availability. | Customer, admin |
| `delete_product` | `product_id`: integer, at least 1 | A deletion message, or a product-not-found error. | Admin |

Each schema requires its input field and rejects additional fields. A blank or whitespace-only search keyword is also rejected by the search function after trimming.

`search_products` only returns IDs and names. The agent must call `check_stock` to obtain stock evidence. Each stock call accepts one `product_id`, so checking two products requires two calls.

Example stock result:

```python
{'ok': True, 'id': 2, 'name': 'Lenovo Laptop', 'stock': 5, 'available': True}
```

## 3. Agent Loop

1. The user enters a request in `main.py`.
2. `run_agent` starts a fresh conversation with the system instructions, current role, and user request.
3. Ollama receives the messages and tool schemas.
4. If the model returns structured tool calls, the application sends each call to `execute_tool` in `harness.py`.
5. The harness checks the tool name, role, permission, and arguments before executing the function.
6. The application adds the tool result to the conversation and asks the model for its next decision.
7. The loop continues until it produces a final answer or reaches a configured limit.

For requests containing `stock`, `available`, or `availability`, the application requires a successful stock result before returning stock information. It formats the final stock summary from recorded `check_stock` results. Only products actually checked are included.

If the model writes a tool request as ordinary JSON text instead of making a structured tool call, the application adds a corrective instruction and continues within the same iteration limit. It does not execute that plain text as a tool call.

## 4. Permission Rule

The role permissions are defined in Python application code:

```python
PERMISSIONS = {
    "customer": {"search_products", "check_stock"},
    "admin": {"search_products", "check_stock", "delete_product"},
}
```

`main.py` uses `CURRENT_ROLE = "customer"`. A user message claiming to be an admin does not change this application value.

The harness checks permission before executing the tool. For example:

```python
execute_tool("delete_product", {"product_id": 2}, "customer")
```

returns:

```python
{'ok': False, 'error': 'Permission denied for this action.'}
```

The product remains in the data. With the `admin` role, the same deletion is allowed.

This demonstrates role-based authorization within the application. It does not implement user accounts, login, or identity verification.

## 5. Safety

### Application-enforced checks

- **Known tools only:** the harness executes functions from its fixed `TOOL_REGISTRY`. Unknown names return `Unknown tool.`
- **Known roles only:** unsupported roles are rejected.
- **Permission checks:** customers cannot execute `delete_product` through the harness.
- **Input validation:** JSON Schema checks required fields, types, minimum values, string length, and extra fields before execution.
- **Controlled errors:** missing products return a structured error. Unexpected exceptions inside a tool return `Tool execution failed.`
- **Bounded execution:** `MAX_ITERATIONS = 6` limits model-loop iterations and `MAX_TOOL_CALLS = 8` limits attempted tool executions per request. Rejected calls also count toward the tool-call limit.
- **Model request timeout:** the Ollama client is configured with a timeout of `120.0` seconds. This is not a total deadline for the complete agent run.
- **Stock evidence:** recognized stock requests use successful tool results to build the displayed stock summary.

The system prompt also tells the model to treat tool output as data, avoid retrying denied actions, and request deletion only when explicitly requested. These are model instructions; the permission and validation rules above are enforced separately by Python code.

If execution stops at a limit, earlier actions are not rolled back. The returned message tells the user to check the preceding results.

### Scope and limitations

- Each user request starts a fresh model conversation, although product changes remain in memory until the process ends.
- The role is selected by the application; this is not a production authentication system.
- Stock-request detection uses a small set of English keywords. It is not a general language understanding or factual verification system.
- A stock request with no successful stock check can reach the iteration limit, including a request for a product that does not exist.
- Stock summaries report the products checked during that request; they do not guarantee that every possible match was checked.
- There is no human confirmation workflow for administrator deletion.

### Test evidence

The recorded runs confirmed product search, stock checks, product-not-found handling, schema loading, customer deletion denial, negative-ID rejection, administrator deletion, controlled handling of a simulated tool exception, and a successful interactive shopping request.

An earlier run using `llama3.2:3b` reached the iteration limit. This demonstrated loop stopping, but that shopping request failed. The successful example below uses `qwen3:4b`.

The eight-tool-call limit is implemented but was not independently exercised in the recorded tests. See [test_log.md](test_log.md) for the recorded commands and outputs.

## 6. Example Run

This is the successful terminal run using `qwen3:4b`:

```text
Safe Shopping Agent
Model: qwen3:4b
Role: customer
Ask about products and stock.
Each request starts a fresh conversation.
Type 'exit' to quit.

You: Find a laptop that is currently in stock.

[Agent iteration 1]
Tool request: search_products({'keyword': 'laptop'})
Tool result: {'ok': True, 'products': [{'id': 1, 'name': 'Dell Laptop'}, {'id': 2, 'name': 'Lenovo Laptop'}]}

[Agent iteration 2]
Tool request: check_stock({'product_id': 1})
Tool result: {'ok': True, 'id': 1, 'name': 'Dell Laptop', 'stock': 0, 'available': False}

[Agent iteration 3]
Tool request: check_stock({'product_id': 2})
Tool result: {'ok': True, 'id': 2, 'name': 'Lenovo Laptop', 'stock': 5, 'available': True}

[Agent iteration 4]

Assistant: Verified stock results:
- Dell Laptop (ID 1): 0 units, out of stock.
- Lenovo Laptop (ID 2): 5 units, in stock.

You: exit
Goodbye!
```

This run demonstrates search, a stock check for an unavailable product, another stock check for an available product, and a final answer grounded in those results.

## 7. Setup and Run on Windows

### Prerequisites

- Python installed. The development environment used Python 3.14.5.
- PyCharm, or another way to run Python from the project folder.
- Ollama installed and running locally at `http://localhost:11434`.

### Install the model

In PowerShell, run:

```powershell
ollama pull qwen3:4b
```

This is needed once unless the model is removed. Check the installed models with:

```powershell
ollama list
```

### Install the Python dependencies

Open the project folder in PyCharm. In its PowerShell terminal, create a virtual environment if the project does not already have one:

```powershell
python -m venv .venv
```

The `requirements.txt` file contains:

```text
jsonschema
ollama
```

Install into the project's environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

For the PyCharm Run button, select this project's `.venv\Scripts\python.exe` as the project interpreter.

### Start the application

Keep Ollama running, then run from the project folder:

```powershell
.\.venv\Scripts\python.exe main.py
```

If the terminal already has the project environment activated, this is equivalent to:

```powershell
python main.py
```

Enter:

```text
Find a laptop that is currently in stock.
```

Type `exit` to quit. Model responses can take time, depending on the computer. Tool choices and wording can vary between runs.

### Common setup issues

| Issue | What to check |
| --- | --- |
| Cannot connect to Ollama | Make sure Ollama is running locally. |
| Model request fails | Check `ollama list` and confirm `qwen3:4b` is installed. |
| Missing Python module | Install requirements using the same virtual environment that runs the project. |
| Iteration or tool-call limit reached | Read the printed tool results to see which actions completed before the stop. |
