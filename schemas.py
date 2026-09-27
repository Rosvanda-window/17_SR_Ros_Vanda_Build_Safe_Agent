TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Find products by a keyword in their name. "
                "Returns product IDs and names. "
                "Use check_stock to check availability."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Product keyword, such as laptop or mouse.",
                        "minLength": 1,
                        "maxLength": 100,
                    }
                },
                "required": ["keyword"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check the stock and availability of one product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The ID of the product to check.",
                        "minimum": 1,
                    }
                },
                "required": ["product_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_product",
            "description": (
                "Delete one product from the practice catalog. "
                "Only admins are permitted to perform this action."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The ID of the product to delete.",
                        "minimum": 1,
                    }
                },
                "required": ["product_id"],
                "additionalProperties": False,
            },
        },
    },
]