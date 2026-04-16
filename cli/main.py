import time
from typing import Optional
import typer

from cli.registry import registry
from cli.diagnostics import with_diagnostics, DiagnosticResult
from cli.display import render_agent_thought, show_graph_stats, progress_spinner, console

# Main CLI entry point
app = typer.Typer(
    help="Mosaic Framework CLI: Demo & Developer Experience Layer",
    no_args_is_help=True
)

# Global CLI State
state = {"debug": False}

@app.callback()
def main_callback(
    debug: bool = typer.Option(
        False, 
        "--debug", 
        help="Print full execution stack, activate debug diagnostics, and highlight the Open Node being hit."
    )
):
    """
    Global setup for Mosaic CLI.
    """
    state["debug"] = debug
    if state["debug"]:
        console.print("[bold yellow][DEBUG MODE INTERCEPT][/bold yellow] Detailed tracing and stack outputs are enabled.")

# -----------------------------------------------------------------------------
# Demo Capabilities Linked to Open Nodes
# -----------------------------------------------------------------------------

@registry.register_command("debate_demo")
@with_diagnostics(
    hint="Check if your Neo4j Docker container is running on Port 7687.", 
    fallback="Loaded local cache from temp_cache.json."
)
def run_debate():
    """
    Simulates a successful structured debate over the graph.
    """
    if state["debug"]:
        console.print("[yellow][DEBUG][/yellow] Open Node Hit: [bold]run_debate[/bold] (Capability: 'debate_demo')")

    render_agent_thought("research", "Gathering facts about the conflict from knowledge graph...")
    
    with progress_spinner("Querying Neo4j for Conflict Nodes...") as progress:
        progress.add_task("Querying...", total=None)
        time.sleep(2)  # Simulate latency for finding nodes

    render_agent_thought("synthesis", "Synthesizing arguments to form a coherent stance...")
    
    with progress_spinner("Processing triplets and restructuring graph...") as progress:
        progress.add_task("Formatting...", total=None)
        time.sleep(1.5)

    show_graph_stats(nodes=150, edges=432)
    console.print("\n[bold green]✓ Debate framework synthesis complete.[/bold green]")
    return True

@registry.register_command("failing_demo")
@with_diagnostics(
    hint="Check if your Neo4j Docker container is running on Port 7687.", 
    fallback="Loaded local cache from temp_cache.json."
)
def failing_demo():
    """
    Simulates a database failure to showcase the Diagnostic Fallback pattern.
    """
    if state["debug"]:
        console.print("[yellow][DEBUG][/yellow] Open Node Hit: [bold]failing_demo[/bold] (Capability: 'failing_demo')")
    
    # Intentionally trigger the fallback mechanism to demonstrate traceability.
    raise ConnectionError("Attempting to fetch Conflict Nodes.")

# -----------------------------------------------------------------------------
# Typer Commands
# -----------------------------------------------------------------------------

@app.command("run")
def run(
    capability: str = typer.Argument(..., help="The capability registered in the Open Node Map to run. Examples: 'debate_demo', 'failing_demo'")
):
    """
    Dynamically trigger a capability from the registry's Open Nodes.
    """
    func = registry.get_capability(capability)
    
    if func:
        if state["debug"]:
             console.print(f"[blue][INFO][/blue] Invoking capability '{capability}'...")
             
        # Call the registered node
        result = func()
        
        # Check if the fallback intercepted and reported an error object
        if isinstance(result, DiagnosticResult) and not result.success:
            # We can print the debug stack trace if in debug mode and wasn't printed inside
            if state["debug"] and result.stack_trace:
                console.print(f"\n[bold magenta]Uncaught Traceback from {result.function_name}:[/bold magenta]\n{result.stack_trace}")
            raise typer.Exit(code=1)
    else:
        capabilities = registry.available_capabilities
        console.print(f"[bold red]Error:[/bold red] Capability '{capability}' not found in registry.")
        if capabilities:
            console.print(f"Available modules: [cyan]{', '.join(capabilities)}[/cyan]")
        raise typer.Exit(code=1)

@app.command("list-nodes")
def list_nodes():
    """
    List all registered capabilities and modules in the Open Nodes Map.
    """
    nodes = registry.available_capabilities
    if not nodes:
        console.print("No capabilities registered.")
        return
        
    console.print("[bold cyan]Active Open Nodes (Capabilities):[/bold cyan]")
    for node in nodes:
         console.print(f"  - [green]{node}[/green]")
         

if __name__ == "__main__":
    app()
