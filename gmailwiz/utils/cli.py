"""
Command-line interface for GmailWiz.

This module provides a user-friendly CLI for running Gmail analysis
and managing the GmailWiz package functionality.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich import print as rich_print

from ..core.gmail_client import GmailClient
from ..analysis.email_analyzer import EmailAnalyzer
from ..core.config import ConfigManager, setup_logging
from ..models import AnalysisReport

console = Console()


@click.group()
@click.option('--config-file', 
              default='gmail_cleaner_config.json',
              help='Path to configuration file')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='Enable verbose logging')
@click.pass_context
def cli(ctx: click.Context, config_file: str, verbose: bool):
    """
    GmailWiz - A powerful Gmail analysis, management, and automation wizard.
    
    This tool helps you understand your email patterns, identify top senders,
    manage your Gmail storage, and automate email operations.
    """
    # Initialize configuration
    config_manager = ConfigManager(config_file=config_file)
    
    if verbose:
        config_manager.update_config(log_level='DEBUG')
    
    setup_logging(config_manager.get_config())
    
    # Store config manager in context
    ctx.ensure_object(dict)
    ctx.obj['config_manager'] = config_manager


@cli.command()
@click.option('--credentials-file', 
              help='Path to Google OAuth2 credentials JSON file')
@click.pass_context
def setup(ctx: click.Context, credentials_file: Optional[str]):
    """
    Set up GmailWiz with your Google credentials.
    
    This command helps you configure the tool with your Gmail API credentials
    and test the connection to ensure everything is working properly.
    """
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    console.print("\n[bold blue]GmailWiz Setup[/bold blue]")
    console.print("This will help you configure GmailWiz with your Google credentials.\n")
    
    # Handle credentials file
    if credentials_file:
        config_manager.update_config(credentials_file=credentials_file)
        config = config_manager.get_config()
    
    credentials_path = config_manager.get_credentials_path()
    
    if not os.path.exists(credentials_path):
        console.print(f"[red]Credentials file not found: {credentials_path}[/red]")
        console.print("\n[yellow]To get your credentials file:[/yellow]")
        console.print("1. Go to https://console.cloud.google.com/")
        console.print("2. Create a new project or select an existing one")
        console.print("3. Enable the Gmail API")
        console.print("4. Create OAuth2 credentials (Desktop application)")
        console.print("5. Download the credentials JSON file")
        console.print(f"6. Save it as '{credentials_path}'\n")
        return
    
    # Validate credentials
    if not config_manager.validate_credentials():
        console.print(f"[red]Invalid credentials file: {credentials_path}[/red]")
        return
    
    console.print(f"[green]✓[/green] Credentials file found: {credentials_path}")
    
    # Test authentication
    console.print("\n[blue]Testing Gmail connection...[/blue]")
    
    try:
        gmail_client = GmailClient(
            credentials_file=config.credentials_file,
            token_file=config.token_file
        )
        
        if gmail_client.authenticate():
            profile = gmail_client.get_user_profile()
            if profile:
                console.print(f"[green]✓[/green] Successfully connected to Gmail!")
                console.print(f"[green]✓[/green] Email: {profile.get('emailAddress')}")
                console.print(f"[green]✓[/green] Total messages: {profile.get('messagesTotal', 'Unknown')}")
            else:
                console.print("[red]✗[/red] Failed to get user profile")
        else:
            console.print("[red]✗[/red] Authentication failed")
            
    except Exception as error:
        console.print(f"[red]✗[/red] Error: {error}")
        return
    
    # Save configuration
    config_manager.save_configuration()
    console.print(f"\n[green]✓[/green] Configuration saved to {config_manager.config_file}")
    console.print("\n[bold green]Setup complete![/bold green] You can now use GmailWiz.")


@cli.command()
@click.option('--days', '-d', 
              default=30, 
              help='Number of days to analyze (default: 30)')
@click.option('--max-emails', '-m', 
              help='Maximum number of emails to analyze')
@click.option('--output', '-o', 
              help='Output file path')
@click.option('--format', 'output_format',
              type=click.Choice(['json', 'csv', 'excel']),
              default='json',
              help='Output format')
@click.option('--no-cache', 
              is_flag=True, 
              help='Disable caching of email data')
@click.pass_context
def analyze(
    ctx: click.Context,
    days: int,
    max_emails: Optional[int],
    output: Optional[str],
    output_format: str,
    no_cache: bool
):
    """
    Analyze your Gmail inbox and generate sender statistics.
    
    This command fetches emails from your Gmail inbox, analyzes sender patterns,
    and generates comprehensive statistics about your email usage.
    """
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    if no_cache:
        config_manager.update_config(enable_cache=False)
        config = config_manager.get_config()
    
    console.print(f"\n[bold blue]Analyzing Gmail inbox[/bold blue]")
    console.print(f"Date range: Last {days} days")
    
    if max_emails:
        console.print(f"Maximum emails: {max_emails}")
    
    # Initialize Gmail client
    try:
        gmail_client = GmailClient(
            credentials_file=config.credentials_file,
            token_file=config.token_file
        )
        
        if not gmail_client.authenticate():
            console.print("[red]Failed to authenticate with Gmail[/red]")
            return
            
    except Exception as error:
        console.print(f"[red]Error initializing Gmail client: {error}[/red]")
        return
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Initialize analyzer
    analyzer = EmailAnalyzer(gmail_client)
    
    try:
        # Run analysis
        with console.status("[bold green]Fetching and analyzing emails..."):
            report = analyzer.analyze_emails_from_date_range(
                start_date=start_date,
                end_date=end_date,
                max_emails=max_emails or config.default_max_emails,
                batch_size=config.default_batch_size
            )
        
        # Display results
        _display_analysis_results(report)
        
        # Save results
        if output:
            output_path = output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gmail_analysis_{timestamp}.{output_format}"
            output_path = config_manager.get_output_path(filename)
        
        _save_analysis_results(report, output_path, output_format, analyzer)
        console.print(f"\n[green]✓[/green] Results saved to: {output_path}")
        
    except Exception as error:
        console.print(f"[red]Analysis failed: {error}[/red]")
        raise click.ClickException(str(error))


@cli.command()
@click.option('--sender', '-s', 
              help='Filter by specific sender email')
@click.option('--limit', '-l', 
              default=20, 
              help='Number of top senders to show')
@click.pass_context
def top_senders(ctx: click.Context, sender: Optional[str], limit: int):
    """
    Show top email senders by count and storage usage.
    
    This command provides a quick overview of your most active email senders
    without performing a full analysis.
    """
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    # This would typically load from cache or prompt for analysis
    console.print("[yellow]This feature requires cached analysis data.[/yellow]")
    console.print("Please run 'gmail-cleaner analyze' first.")


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """
    Show GmailWiz status and configuration.
    
    This command displays the current configuration, authentication status,
    and any cached analysis data information.
    """
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    console.print("\n[bold blue]GmailWiz Status[/bold blue]\n")
    
    # Configuration status
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Credentials file", config.credentials_file)
    config_table.add_row("Token file", config.token_file)
    config_table.add_row("Output directory", config.output_directory)
    config_table.add_row("Default max emails", str(config.default_max_emails))
    config_table.add_row("Cache enabled", str(config.enable_cache))
    
    console.print(config_table)
    
    # Authentication status
    console.print("\n[bold]Authentication Status[/bold]")
    
    credentials_exists = os.path.exists(config_manager.get_credentials_path())
    token_exists = os.path.exists(config_manager.get_token_path())
    
    if credentials_exists:
        console.print("[green]✓[/green] Credentials file found")
    else:
        console.print("[red]✗[/red] Credentials file not found")
    
    if token_exists:
        console.print("[green]✓[/green] Authentication token exists")
    else:
        console.print("[yellow]![/yellow] No authentication token (run setup)")


def _display_analysis_results(report: AnalysisReport) -> None:
    """Display analysis results in the console."""
    console.print(f"\n[bold green]Analysis Complete![/bold green]")
    console.print(f"Analyzed {report.total_emails_analyzed:,} emails")
    console.print(f"Date range: {report.date_range_start.date()} to {report.date_range_end.date()}")
    console.print(f"Found {len(report.sender_statistics)} unique senders")
    console.print(f"Total storage: {report.total_storage_used_bytes / (1024**3):.2f} GB")
    
    # Top senders by count
    console.print("\n[bold]Top Senders by Email Count[/bold]")
    count_table = Table()
    count_table.add_column("Sender", style="cyan")
    count_table.add_column("Emails", justify="right", style="green")
    count_table.add_column("Storage (MB)", justify="right", style="yellow")
    count_table.add_column("Read %", justify="right", style="blue")
    
    for sender in report.get_top_senders_by_count(10):
        count_table.add_row(
            sender.sender_email,
            str(sender.total_emails),
            f"{sender.total_size_bytes / (1024**2):.1f}",
            f"{sender.read_percentage:.1f}%"
        )
    
    console.print(count_table)
    
    # Top senders by storage
    console.print("\n[bold]Top Senders by Storage Usage[/bold]")
    storage_table = Table()
    storage_table.add_column("Sender", style="cyan")
    storage_table.add_column("Storage (MB)", justify="right", style="yellow")
    storage_table.add_column("Emails", justify="right", style="green")
    storage_table.add_column("Avg Size (KB)", justify="right", style="blue")
    
    for sender in report.get_top_senders_by_size(10):
        storage_table.add_row(
            sender.sender_email,
            f"{sender.total_size_bytes / (1024**2):.1f}",
            str(sender.total_emails),
            f"{sender.average_size_bytes / 1024:.1f}"
        )
    
    console.print(storage_table)


def _save_analysis_results(
    report: AnalysisReport,
    output_path: str,
    output_format: str,
    analyzer: EmailAnalyzer
) -> None:
    """Save analysis results to file."""
    if output_format == 'json':
        report.save_to_json(output_path)
    elif output_format == 'csv':
        df = analyzer.export_to_dataframe()
        df.to_csv(output_path, index=False)
    elif output_format == 'excel':
        df = analyzer.export_to_dataframe()
        df.to_excel(output_path, index=False)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as error:
        console.print(f"\n[red]Unexpected error: {error}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
