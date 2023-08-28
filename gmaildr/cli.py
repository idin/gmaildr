"""
Command-line interface for GmailDr.

This module provides a user-friendly CLI for running Gmail analysis
and managing the GmailDr package functionality.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
from rich import print as rich_print
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

from .core.client.gmail_client import GmailClient
from .core.config.config import ConfigManager, GmailConfig, setup_logging
from .core.gmail.email_analyzer import EmailAnalyzer

console = Console()


@click.group()
@click.option(
    '--config-file',
    default='gmail_cleaner_config.json',
    help='Path to configuration file'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging'
)
@click.pass_context
def cli(ctx: click.Context, config_file: str, verbose: bool):
    """
    GmailDr - A powerful Gmail analysis, management, and automation wizard.
    
    This tool helps you understand your email patterns, identify top senders,
    manage your Gmail storage, and automate email operations.
    
    Args:
        ctx: Click context object for storing configuration.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
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
@click.option(
    '--credentials-file',
    help='Path to Google OAuth2 credentials JSON file'
)
@click.pass_context
def _display_credentials_instructions(ctx, credentials_file: str) -> None:
    """Display instructions for obtaining Google credentials.
    
    Args:
        credentials_path: Path where credentials file should be saved.
    """
    console.print(f"[red]Credentials file not found: {credentials_file}[/red]")
    console.print("\n[yellow]To get your credentials file:[/yellow]")
    console.print("1. Go to https://console.cloud.google.com/")
    console.print("2. Create a new project or select an existing one")
    console.print("3. Enable the Gmail API")
    console.print("4. Create OAuth2 credentials (Desktop application)")
    console.print("5. Download the credentials JSON file")
    console.print(f"6. Save it as '{credentials_file}'\n")


def _test_gmail_connection(config_manager: 'ConfigManager') -> bool:
    """Test Gmail connection and display results.
    
    Args:
        config_manager: Configuration manager instance.
        
    Returns:
        True if connection successful, False otherwise.
    """
    console.print("\n[blue]Testing Gmail connection...[/blue]")
    
    try:
        config = config_manager.get_config()
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
                return True
            else:
                console.print("[red]✗[/red] Failed to get user profile")
                return False
        else:
            console.print("[red]✗[/red] Authentication failed")
            return False
            
    except Exception as error:
        console.print(f"[red]✗[/red] Error: {error}")
        return False


def _initialize_gmail_client(config: 'GmailConfig') -> Optional['GmailClient']:
    """Initialize and authenticate Gmail client.
    
    Args:
        config: Gmail configuration instance.
        
    Returns:
        Authenticated Gmail client or None if failed.
    """
    try:
        gmail_client = GmailClient(
            credentials_file=config.credentials_file,
            token_file=config.token_file
        )
        
        if not gmail_client.authenticate():
            console.print("[red]Failed to authenticate with Gmail[/red]")
            return None
            
        return gmail_client
        
    except Exception as error:
        console.print(f"[red]Error initializing Gmail client: {error}[/red]")
        return None


def _run_email_analysis(
    analyzer: 'EmailAnalyzer',
    days: int,
    max_emails: Optional[int],
    config: 'GmailConfig'
) -> dict:
    """Run email analysis and return results.
    
    Args:
        analyzer: Email analyzer instance.
        days: Number of days to analyze.
        max_emails: Maximum number of emails to analyze.
        config: Gmail configuration instance.
        
    Returns:
        Analysis results dictionary.
    """
    with console.status("[bold green]Fetching and analyzing emails..."):
        report = analyzer.analyze(
            days=days,
            max_emails=max_emails or config.default_max_emails
        )
    return report


def _generate_output_path(
    output: Optional[str],
    output_format: str,
    config_manager: 'ConfigManager'
) -> str:
    """Generate output file path for analysis results.
    
    Args:
        output: User-specified output path.
        output_format: Output format (json, csv, excel).
        config_manager: Configuration manager instance.
        
    Returns:
        Output file path.
    """
    if output:
        return output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gmail_analysis_{timestamp}.{output_format}"
        return config_manager.get_output_path(filename)


def setup(ctx: click.Context, credentials_file: Optional[str]):
    """
    Set up GmailDr with your Google credentials.
    
    This command helps you configure the tool with your Gmail API credentials
    and test the connection to ensure everything is working properly.
    
    Args:
        ctx: Click context object for storing configuration.
        credentials_file: Path to Google OAuth2 credentials JSON file.
    """
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    console.print("\n[bold blue]GmailDr Setup[/bold blue]")
    console.print("This will help you configure GmailDr with your Google credentials.\n")
    
    # Handle credentials file
    if credentials_file:
        config_manager.update_config(credentials_file=credentials_file)
        config = config_manager.get_config()
    
    credentials_path = config_manager.get_credentials_path()
    
    if not os.path.exists(credentials_path):
        _display_credentials_instructions(credentials_path)
        return
    
    # Validate credentials
    if not config_manager.validate_credentials():
        console.print(f"[red]Invalid credentials file: {credentials_path}[/red]")
        return
    
    console.print(f"[green]✓[/green] Credentials file found: {credentials_path}")
    
    # Test authentication
    if not _test_gmail_connection(config_manager):
        return
    
    # Save configuration
    config_manager.save_configuration()
    console.print(f"\n[green]✓[/green] Configuration saved to {config_manager.config_file}")
    console.print("\n[bold green]Setup complete![/bold green] You can now use GmailDr.")


@cli.command()
@click.option(
    '--days', '-d',
    default=30,
    help='Number of days to analyze (default: 30)'
)
@click.option(
    '--max-emails', '-m',
    help='Maximum number of emails to analyze'
)
@click.option(
    '--output', '-o',
    help='Output file path'
)
@click.option(
    '--format', 'output_format',
    type=click.Choice(['json', 'csv', 'excel']),
    default='json',
    help='Output format'
)
@click.option(
    '--no-cache',
    is_flag=True,
    help='Disable caching of email data'
)
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
    
    Args:
        ctx: Click context object for storing configuration.
        days: Number of days to analyze.
        max_emails: Maximum number of emails to analyze.
        output: Output file path.
        output_format: Output format (json, csv, excel).
        no_cache: Disable caching of email data.
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
    gmail_client = _initialize_gmail_client(config)
    if not gmail_client:
        return
    
    # Initialize analyzer
    analyzer = EmailAnalyzer(
        credentials_file=config.credentials_file,
        token_file=config.token_file,
        enable_cache=not no_cache,
        verbose=config.verbose
    )
    
    try:
        # Run analysis
        report = _run_email_analysis(analyzer, days, max_emails, config)
        
        # Display results
        _display_analysis_results(report)
        
        # Save results
        output_path = _generate_output_path(output, output_format, config_manager)
        _save_analysis_results(report, output_path, output_format, analyzer)
        console.print(f"\n[green]✓[/green] Results saved to: {output_path}")
        
    except Exception as error:
        console.print(f"[red]Analysis failed: {error}[/red]")
        raise click.ClickException(str(error))


@cli.command()
@click.option(
    '--sender', '-s',
    help='Filter by specific sender email'
)
@click.option(
    '--limit', '-l',
    default=20,
    help='Number of top senders to show'
)
@click.pass_context
def top_senders(ctx: click.Context, sender: Optional[str], limit: int):
    """
    Show top email senders by count and storage usage.
    
    This command provides a quick overview of your most active email senders
    without performing a full analysis.
    
    Args:
        ctx: Click context object for storing configuration.
        sender: Filter by specific sender email.
        limit: Number of top senders to show.
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
    Show GmailDr status and configuration.
    
    This command displays the current configuration, authentication status,
    and any cached analysis data information.
    
    Args:
        ctx: Click context object for storing configuration.
    """
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    console.print("\n[bold blue]GmailDr Status[/bold blue]\n")
    
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


def _display_analysis_results(report: dict) -> None:
    """Display analysis results in the console."""
    console.print(f"\n[bold green]Analysis Complete![/bold green]")
    console.print(f"Analyzed {report.get('total_emails', 0):,} emails")
    
    date_range = report.get('date_range', {})
    if date_range:
        start_date = date_range.get('start', 'Unknown')
        end_date = date_range.get('end', 'Unknown')
        console.print(f"Date range: {start_date} to {end_date}")
    
    # Display basic statistics
    emails_df = report.get('emails_df')
    if emails_df is not None and not emails_df.empty:
        console.print(f"Found {len(emails_df['sender_email'].unique())} unique senders")
        total_size = emails_df['size_kb'].sum() if 'size_kb' in emails_df.columns else 0
        console.print(f"Total storage: {total_size / (1024**2):.2f} MB")
    
    console.print("\n[bold]Analysis completed successfully![/bold]")


def _save_analysis_results(
    report: dict,
    output_path: str,
    output_format: str,
    analyzer: 'EmailAnalyzer'
) -> None:
    """Save analysis results to file."""
    if output_format == 'json':
        with open(output_path, 'w') as f:
            json.dump(report, f, default=str, indent=2)
    elif output_format == 'csv':
        emails_df = report.get('emails_df')
        if emails_df is not None:
            emails_df.to_csv(output_path, index=False)
    elif output_format == 'excel':
        emails_df = report.get('emails_df')
        if emails_df is not None:
            emails_df.to_excel(output_path, index=False)


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
