def generate_query(table_name, column_name, entries):
    query = f"SELECT * FROM SQL_EDITOR_{table_name}_TABLE \nWHERE "
    conditions = []

    for entry in entries:
        conditions.append(f"LOWER({column_name}) LIKE LOWER('%{entry}%')")

    query += " OR ".join(conditions) + ";"
    return query