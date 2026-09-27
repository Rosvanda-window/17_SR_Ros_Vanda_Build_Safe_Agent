from jsonschema import validate, ValidationError

from schemas import TOOL_SCHEMAS
from tools import search_products, check_stock, delete_product


# Map approved tool names to their actual Python functions.
TOOL_REGISTRY = {
    "search_products": search_products,
    "check_stock": check_stock,
    "delete_product": delete_product,
}

# Define which tools each role may execute.
PERMISSIONS = {
    "customer": {"search_products", "check_stock"},
    "admin": {"search_products", "check_stock", "delete_product"},
}

# Map each tool name to its input schema.
INPUT_SCHEMAS = {
    tool["function"]["name"]: tool["function"]["parameters"]
    for tool in TOOL_SCHEMAS
}


def execute_tool(tool_name: str, arguments: dict, role: str) -> dict:
    """Check a tool request and execute it only when allowed."""

    # 1. Reject unknown tool names.
    if not isinstance(tool_name, str) or tool_name not in TOOL_REGISTRY:
        return {"ok": False, "error": "Unknown tool."}

    # 2. Reject unknown roles.
    if not isinstance(role, str) or role not in PERMISSIONS:
        return {"ok": False, "error": "Unknown role."}

    # 3. Check permission before executing anything.
    if tool_name not in PERMISSIONS[role]:
        return {
            "ok": False,
            "error": "Permission denied for this action.",
        }

    # 4. Check arguments against the tool's schema.
    try:
        validate(
            instance=arguments,
            schema=INPUT_SCHEMAS[tool_name],
        )
    except ValidationError as error:
        return {
            "ok": False,
            "error": f"Invalid arguments: {error.message}",
        }

    # 5. Execute the approved tool and handle unexpected failures.
    try:
        tool_function = TOOL_REGISTRY[tool_name]
        return tool_function(**arguments)
    except Exception:
        return {
            "ok": False,
            "error": "Tool execution failed.",
        }