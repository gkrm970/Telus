def to_avro_schema(node, name):
    if isinstance(node, dict):
        fields = []
        for k, v in node.items():
            schema = to_avro_schema(v, k)
            if schema is not None:
                fields.append({"name": k, "type": schema})
        return {"name": name, "type": "record", "fields": fields}
    elif isinstance(node, list):
        items = []
        for item in node:
            schema = to_avro_schema(item, name)
            if schema is not None:
                items.append(schema)
        if len(items) > 0:
            return {"type": "array", "items": items[0]}
        else:
            return None
    elif isinstance(node, str):
        return "string"
    elif isinstance(node, bool):
        return "boolean"
    elif isinstance(node, int):
        return "int"
    elif isinstance(node, float):
        return "float"
    elif node is None:
        return "null"
    else:
        return None


def infer_avro_schema(data, name):
    schema = to_avro_schema(data, name)
    if schema is None:
        raise ValueError("Could not infer schema from data")
    return schema
