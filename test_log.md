# Safe Shopping Agent Test Log

## 1. Test Environment

- Operating system: Windows
- IDE: PyCharm
- Python version: 3.14.5
- Virtual environment: .venv
- Successful agent model: qwen3:4b
- Earlier troubleshooting model: llama3.2:3b
- Python packages: ollama, jsonschema
- Product storage: in-memory Python dictionary
- Test date: 2026-09-27

## 2. Initial Product Data

| Product ID | Product name | Stock |
|---|---|---:|
| 1 | Dell Laptop | 0 |
| 2 | Lenovo Laptop | 5 |
| 3 | Wireless Mouse | 12 |

Product data resets when a new Python process starts.

## 3. Test Summary

| ID | Test | Observed result | Status |
|---|---|---|---|
| T01 | Search for laptops | Returned Dell and Lenovo | Passed |
| T02 | Check an existing product | Lenovo stock was 5, available True | Passed |
| T03 | Check a missing product | Returned Product not found | Passed |
| T04 | Load tool schemas | All three tool names loaded | Passed |
| T05 | Customer checks stock through harness | Allowed and returned correct stock | Passed |
| T06 | Customer attempts deletion | Denied; product remained | Passed |
| T07 | Negative product ID | Rejected by schema validation | Passed |
| T08 | Admin deletes a product | Deleted; subsequent lookup failed | Passed |
| T09 | Maximum iteration limit | Earlier llama3.2 run stopped after six iterations | Passed |
| T10 | Interactive Qwen3 agent and exit | Completed search and stock checks, then exited | Passed |
| T11 | Unexpected tool exception | Returned controlled error without crashing | Passed |

## 4. Detailed Tests

### T01 — Search for Products

Purpose: Verify that keyword search returns matching products.

Command:

```powershell
python -c "from tools import search_products; print(search_products('Laptop'))"
```

Actual output:

```text
{'ok': True, 'products': [{'id': 1, 'name': 'Dell Laptop'}, {'id': 2, 'name': 'Lenovo Laptop'}]}
```

Result: Passed. Both product names contain the keyword.

### T02 — Check an Existing Product

Purpose: Verify the stock information for product 2.

Command:

```powershell
python -c "from tools import check_stock; print(check_stock(2))"
```

Actual result, captured alongside T03 in the original terminal run:

```text
{'ok': True, 'id': 2, 'name': 'Lenovo Laptop', 'stock': 5, 'available': True}
```

Result: Passed. Lenovo Laptop has 5 units available.

### T03 — Check a Missing Product

Purpose: Verify that a nonexistent ID returns a controlled error.

Command:

```powershell
python -c "from tools import check_stock; print(check_stock(999))"
```

Actual result, captured alongside T02 in the original terminal run:

```text
{'ok': False, 'error': 'Product not found.'}
```

Result: Passed. The function reported the missing product without crashing.

### T04 — Load Tool Schemas

Purpose: Verify that Python can import the three tool definitions.

Command:

```powershell
python -c "from schemas import TOOL_SCHEMAS; print([tool['function']['name'] for tool in TOOL_SCHEMAS])"
```

Actual output:

```text
['search_products', 'check_stock', 'delete_product']
```

Result: Passed.

This test checks that the definitions load. It does not, by itself,
prove that all schema constraints are enforced.

### T05 — Customer Checks Stock Through the Harness

Purpose: Verify that the harness permits an allowed customer action.

Command:

```powershell
python -c "from harness import execute_tool; print(execute_tool('check_stock', {'product_id': 2}, 'customer'))"
```

Actual output:

```text
{'ok': True, 'id': 2, 'name': 'Lenovo Laptop', 'stock': 5, 'available': True}
```

Result: Passed. The permitted action executed successfully.

### T06 — Customer Attempts Deletion

Purpose: Verify that customer deletion is blocked before the product
is removed.

Command:

```powershell
python -c "from harness import execute_tool; print(execute_tool('delete_product', {'product_id': 2}, 'customer')); print(execute_tool('check_stock', {'product_id': 2}, 'customer'))"
```

Actual output:

```text
{'ok': False, 'error': 'Permission denied for this action.'}
{'ok': True, 'id': 2, 'name': 'Lenovo Laptop', 'stock': 5, 'available': True}
```

Result: Passed.

The deletion was denied, and the following lookup confirmed that
product 2 remained in the catalog.

### T07 — Reject a Negative Product ID

Purpose: Verify that the harness enforces the schema's minimum ID value.

Command:

```powershell
python -c "from harness import execute_tool; print(execute_tool('check_stock', {'product_id': -1}, 'customer'))"
```

Actual output:

```text
{'ok': False, 'error': 'Invalid arguments: -1 is less than the minimum of 1'}
```

Result: Passed. The invalid argument was rejected before tool execution.

### T08 — Admin Deletes a Product

Purpose: Verify that an admin can delete a practice product.

Command:

```powershell
python -c "from harness import execute_tool; print(execute_tool('delete_product', {'product_id': 2}, 'admin')); print(execute_tool('check_stock', {'product_id': 2}, 'admin'))"
```

Actual output:

```text
{'ok': True, 'message': 'Deleted Lenovo Laptop.'}
{'ok': False, 'error': 'Product not found.'}
```

Result: Passed.

Both calls ran in the same process. The second call confirmed that
the product had been removed.

This was a direct harness test using an application-supplied admin
role. It did not test authentication or an LLM-driven admin session.

### T09 — Maximum Iteration Limit

Purpose: Verify that an unsuccessful agent run cannot continue forever.

Model used for this earlier test: llama3.2:3b.

Request:

```text
Find a laptop that is currently in stock.
```

Observed terminal output:

```text
[Agent iteration 1]
Tool request: search_products({'keyword': 'laptop'})
Tool result: {'ok': True, 'products': [{'id': 1, 'name': 'Dell Laptop'}, {'id': 2, 'name': 'Lenovo Laptop'}]}

[Agent iteration 2]
Answer blocked: no actual stock check was completed.

[Agent iteration 3]
The model wrote a tool request as text. Asking it to correct the format.

[Agent iteration 4]
Answer blocked: no actual stock check was completed.

[Agent iteration 5]
Answer blocked: no actual stock check was completed.

[Agent iteration 6]
The model wrote a tool request as text. Asking it to correct the format.
Stopped: iteration limit reached. Earlier actions may have completed; check the results above.
```

Result: Passed for the iteration-limit control.

The shopping task did not succeed in this run. The application blocked
unsupported stock answers and stopped after six iterations. The model
was subsequently changed to qwen3:4b.

### T10 — Interactive Agent Loop and Exit

Purpose: Verify the complete application with a real user request,
multiple model-selected tool calls, observations, and terminal exit.

Command:

```powershell
python main.py
```

Actual session:

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

Result: Passed.

The model:
1. Requested a product search.
2. Used a returned ID to check Dell's stock.
3. Continued to Lenovo after observing Dell's zero stock.
4. Returned a response without further tool calls.

The application formatted the final stock quantities from actual tool
results. The exit command ended the terminal session cleanly.

### T11 — Unexpected Tool Exception

Purpose: Verify that an unexpected tool exception is caught by the
harness and returned as a controlled error.

Command entered in PowerShell:

```powershell
@'
from unittest.mock import Mock, patch
from harness import execute_tool, TOOL_REGISTRY

failing_tool = Mock(side_effect=RuntimeError("Simulated failure"))

with patch.dict(TOOL_REGISTRY, {"check_stock": failing_tool}):
    result = execute_tool(
        "check_stock",
        {"product_id": 2},
        "customer",
    )
    print(result)
'@ | python
```

Actual output:

```text
{'ok': False, 'error': 'Tool execution failed.'}
```

Result: Passed.

The mock raised a RuntimeError. The harness caught it and returned a
controlled result. The original registry entry was restored when the
patch context ended.

## 5. Test Coverage Notes

- Permission and invalid-input tests were performed directly against
  the harness, independently of the model's behavior.
- The successful Qwen3 run demonstrated the real search-to-stock agent loop.
- The six-iteration limit was observed during an earlier llama3.2 run.
- The separate eight-tool-attempt limit is implemented but was not
  independently triggered in these tests.
- Timeout and connection-error handling were not deliberately triggered.
- Not every schema constraint was tested individually.
- The stock-answer safeguard uses simple English keyword detection
  and reports only products actually checked.
- Roles are supplied by application code. This project has no login system.
- These results demonstrate the listed cases, not guaranteed behavior
  for every possible user request.