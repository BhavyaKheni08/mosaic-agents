import functools
import traceback
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.panel import Panel

console = Console()

class DiagnosticResult(BaseModel):
    """
    Standard Result Object for the Diagnostic Fallback pattern.
    """
    success: bool
    function_name: str
    file_name: str
    input_parameters: Dict[str, Any]
    error_message: Optional[str] = None
    fallback_taken: Optional[str] = None
    hint: Optional[str] = None
    stack_trace: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

def render_diagnostic(result: DiagnosticResult, debug: bool = False):
    """
    Renders the diagnostic error securely using Rich Panels.
    """
    if result.success:
        return
    
    content = f"[bold red]❌ CRITICAL ERROR in {result.file_name}[/bold red]\n"
    content += f"[bold blue]Function:[/bold blue] {result.function_name}\n"
    content += f"[bold blue]Context / Inputs:[/bold blue] {result.input_parameters}\n"
    
    if result.error_message:
         content += f"[bold red]Error:[/bold red] {result.error_message}\n"
    if result.fallback_taken:
        content += f"[bold yellow]Fallback:[/bold yellow] {result.fallback_taken}\n"
    if result.hint:
        content += f"[bold cyan]Hint:[/bold cyan] {result.hint}\n"
        
    if debug and result.stack_trace:
        content += f"\n[bold magenta]Stack Trace:[/bold magenta]\n{result.stack_trace}"

    panel = Panel(content, title="Diagnostic Fallback Initiated", border_style="red")
    console.print(panel)

def with_diagnostics(hint: str = "Check your configuration or inputs.", fallback: str = "Fallback mechanism invoked."):
    """
    Decorator enforcing the 'Diagnostic Fallback' pattern.
    If the function fails, it catches the error and returns a DiagnosticResult.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Return standard Result Object wrapper (assuming func returns normally)
                return func(*args, **kwargs)
            except Exception as e:
                # Create a DiagnosticResult
                result = DiagnosticResult(
                    success=False,
                    function_name=func.__name__,
                    file_name=func.__code__.co_filename.split('/')[-1],
                    input_parameters={"args": str(args), "kwargs": str(kwargs)},
                    error_message=str(e),
                    fallback_taken=fallback,
                    hint=hint,
                    stack_trace=traceback.format_exc()
                )
                
                # Check for debug flag in a naive way or let the caller decide to render it.
                # Here we just render it directly for convenience in the CLI.
                # In a real setup we might retrieve the `debug` state dynamically.
                render_diagnostic(result)
                return result
        return wrapper
    return decorator
