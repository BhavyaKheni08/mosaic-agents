from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Initialize global rich Console for the CLI
console = Console()

def render_agent_thought(agent_type: str, thought: str):
    """
    Renders an agent's internal thought process to the terminal.
    Uses distinct color palettes based on the agent type.
    """
    color = "white"
    agent_type_lower = agent_type.lower()
    
    # Specific colors corresponding to the agent type visually orchestrating
    if "research" in agent_type_lower:
        color = "bold cyan"
    elif "synthesis" in agent_type_lower:
         color = "bold magenta"
    elif "critic" in agent_type_lower:
         color = "bold yellow"
    elif "auditor" in agent_type_lower:
         color = "bold green"
        
    panel = Panel(
        f"[{color}]{thought}[/{color}]", 
        title=f"🧠 {agent_type.capitalize()} Agent Thought", 
        border_style=color
    )
    console.print(panel)

def show_graph_stats(nodes: int, edges: int):
    """
    Displays the Neo4j or underlying graph stats inside a Live Table.
    """
    table = Table(title="Knowledge Graph Status", border_style="blue")
    table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Active Nodes", str(nodes))
    table.add_row("Relationships (Edges)", str(edges))

    console.print(table)

def progress_spinner(description: str):
    """
    Utility returning a rich.progress context manager configured 
    as an indeterminate spinner for long-running processes (like Graph Gen).
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    )
