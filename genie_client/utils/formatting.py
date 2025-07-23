def format_results_to_markdown(columns: list, data: list, max_rows: int = 100) -> str:
    """
    Converts query results to a markdown table with smart formatting
    
    Args:
        columns: List of column names
        data: List of rows (each row is a list of values)
        max_rows: Maximum rows to include in the output
        
    Returns:
        Markdown-formatted table string
    """
    if not columns or not data:
        return "No results found"
    
    # Truncate large datasets
    truncated = False
    if len(data) > max_rows:
        data = data[:max_rows]
        truncated = True
    
    # Create header
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    
    # Create rows
    rows = []
    for row in data:
        # Format each cell
        formatted_row = []
        for value in row:
            # Format numbers
            if isinstance(value, (int, float)):
                # Format large numbers with commas
                if abs(value) >= 1000:
                    try:
                        value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                    except:
                        pass
            formatted_row.append(str(value))
        rows.append("| " + " | ".join(formatted_row) + " |")
    
    # Build final table
    table = "\n".join([header, separator] + rows)
    
    # Add truncation note
    if truncated:
        table += f"\n\n*Showing first {max_rows} of {len(data)} rows*"
    
    return table