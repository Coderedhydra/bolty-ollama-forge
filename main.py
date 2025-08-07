#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
import time
import logging
from colorama import init, Fore, Style, Back
from tabulate import tabulate
from typing import Dict, List
import os

from config import config
from link_extractor import LinkExtractor
from vulnerability_scanner import VulnerabilityScanner
from llm_clients import LLMManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.verbose else logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vulnerability_scan.log')
    ]
)

logger = logging.getLogger(__name__)

class VulnScannerCLI:
    def __init__(self):
        self.banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    AI-Powered Vulnerability Scanner             ║
║                           Version 1.0                           ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
    
    def print_banner(self):
        print(self.banner)
        print(f"{Fore.YELLOW}[*] Initializing AI-powered vulnerability scanner...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Configuration loaded{Style.RESET_ALL}")
        
        # Show available LLM providers
        llm_manager = LLMManager()
        available_clients = list(llm_manager.clients.keys())
        print(f"{Fore.GREEN}[✓] Available AI models: {', '.join(available_clients)}{Style.RESET_ALL}")
        
        if config.gemini_api_key:
            print(f"{Fore.GREEN}[✓] Gemini API configured{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] Gemini API key not configured{Style.RESET_ALL}")
        
        print()
    
    def print_crawl_summary(self, crawl_result: Dict):
        """Print crawling summary"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"            CRAWLING SUMMARY")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}Target URL:{Style.RESET_ALL} {crawl_result['base_url']}")
        print(f"{Fore.GREEN}Pages Visited:{Style.RESET_ALL} {crawl_result['visited_pages']}")
        print(f"{Fore.GREEN}Links Found:{Style.RESET_ALL} {crawl_result['total_links']}")
        print(f"{Fore.GREEN}Forms Found:{Style.RESET_ALL} {crawl_result['total_forms']}")
        
        # Show interesting endpoints
        interesting = crawl_result.get('interesting_endpoints', [])
        if interesting:
            print(f"\n{Fore.YELLOW}[*] Interesting endpoints found:{Style.RESET_ALL}")
            for endpoint in interesting[:5]:  # Show top 5
                print(f"  • {endpoint['url']} ({endpoint['type']})")
            if len(interesting) > 5:
                print(f"  ... and {len(interesting) - 5} more")
        
        print()
    
    def print_ai_analysis(self, ai_analysis: Dict):
        """Print AI analysis results"""
        if "error" in ai_analysis:
            print(f"{Fore.RED}[✗] AI Analysis failed: {ai_analysis['error']}{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"            AI ANALYSIS RESULTS")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        # Priority endpoints
        priority_endpoints = ai_analysis.get('priority_endpoints', [])
        if priority_endpoints:
            print(f"\n{Fore.YELLOW}[*] High Priority Targets:{Style.RESET_ALL}")
            headers = ["URL", "Priority", "Vulnerability Types", "Reasoning"]
            table_data = []
            
            for endpoint in priority_endpoints[:10]:
                table_data.append([
                    endpoint['url'][:50] + "..." if len(endpoint['url']) > 50 else endpoint['url'],
                    f"{endpoint['priority']}/10",
                    ", ".join(endpoint['vulnerability_types'][:2]),
                    endpoint['reasoning'][:40] + "..." if len(endpoint['reasoning']) > 40 else endpoint['reasoning']
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Form analysis
        form_analysis = ai_analysis.get('form_analysis', [])
        if form_analysis:
            print(f"\n{Fore.YELLOW}[*] Form Risk Analysis:{Style.RESET_ALL}")
            headers = ["Form URL", "Risk Level", "Recommended Tests"]
            table_data = []
            
            for form in form_analysis[:5]:
                table_data.append([
                    form['form_url'][:50] + "..." if len(form['form_url']) > 50 else form['form_url'],
                    self._colorize_risk(form['risk_level']),
                    ", ".join(form['recommended_tests'][:2])
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Testing strategy
        strategy = ai_analysis.get('testing_strategy', '')
        if strategy:
            print(f"\n{Fore.YELLOW}[*] AI Recommended Testing Strategy:{Style.RESET_ALL}")
            print(f"  {strategy}")
        
        print()
    
    def _colorize_risk(self, risk_level: str) -> str:
        """Colorize risk level text"""
        if risk_level.lower() == 'high':
            return f"{Fore.RED}{risk_level}{Style.RESET_ALL}"
        elif risk_level.lower() == 'medium':
            return f"{Fore.YELLOW}{risk_level}{Style.RESET_ALL}"
        else:
            return f"{Fore.GREEN}{risk_level}{Style.RESET_ALL}"
    
    def _colorize_severity(self, severity: str) -> str:
        """Colorize severity text"""
        if severity == 'Critical':
            return f"{Back.RED}{Fore.WHITE}{severity}{Style.RESET_ALL}"
        elif severity == 'High':
            return f"{Fore.RED}{severity}{Style.RESET_ALL}"
        elif severity == 'Medium':
            return f"{Fore.YELLOW}{severity}{Style.RESET_ALL}"
        else:
            return f"{Fore.GREEN}{severity}{Style.RESET_ALL}"
    
    def print_scan_results(self, scan_results: Dict):
        """Print vulnerability scan results"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"            VULNERABILITY SCAN RESULTS")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        if "error" in scan_results:
            print(f"{Fore.RED}[✗] Scan failed: {scan_results['error']}{Style.RESET_ALL}")
            return
        
        total_vulns = scan_results['total_vulnerabilities_found']
        if total_vulns == 0:
            print(f"{Fore.GREEN}[✓] No vulnerabilities found!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.RED}[!] Found {total_vulns} potential vulnerabilities{Style.RESET_ALL}")
        
        # Summary by type
        vuln_by_type = scan_results['vulnerabilities_by_type']
        if vuln_by_type:
            print(f"\n{Fore.YELLOW}[*] Vulnerabilities by Type:{Style.RESET_ALL}")
            for vuln_type, vulns in vuln_by_type.items():
                print(f"  • {vuln_type.replace('_', ' ').title()}: {len(vulns)}")
        
        # Severity breakdown
        scan_summary = scan_results.get('scan_summary', {})
        severity_breakdown = scan_summary.get('severity_breakdown', {})
        if severity_breakdown:
            print(f"\n{Fore.YELLOW}[*] Severity Breakdown:{Style.RESET_ALL}")
            for severity, count in severity_breakdown.items():
                if count > 0:
                    print(f"  • {self._colorize_severity(severity)}: {count}")
        
        # Detailed results
        results = scan_results['results'][:10]  # Show top 10
        if results:
            print(f"\n{Fore.YELLOW}[*] Detailed Results (Top 10):{Style.RESET_ALL}")
            headers = ["URL", "Vulnerability", "Severity", "Injection Point", "Confidence"]
            table_data = []
            
            for result in results:
                table_data.append([
                    result['url'][:40] + "..." if len(result['url']) > 40 else result['url'],
                    result['vulnerability_type'].replace('_', ' ').title(),
                    self._colorize_severity(result['severity']),
                    result['injection_point'],
                    f"{result['confidence']:.2f}"
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        if total_vulns > 10:
            print(f"\n{Fore.YELLOW}[!] Showing top 10 results. See JSON output for complete results.{Style.RESET_ALL}")
        
        print()
    
    def save_results(self, crawl_result: Dict, ai_analysis: Dict, scan_results: Dict, output_file: str):
        """Save results to file"""
        complete_results = {
            'scan_metadata': {
                'timestamp': time.time(),
                'target_url': crawl_result.get('base_url', ''),
                'scanner_version': '1.0',
                'config_used': {
                    'max_depth': config.max_depth,
                    'gemini_model': config.gemini_model,
                    'ollama_model': config.ollama_model
                }
            },
            'crawl_results': crawl_result,
            'ai_analysis': ai_analysis,
            'vulnerability_scan': scan_results
        }
        
        try:
            if output_file.endswith('.json'):
                with open(output_file, 'w') as f:
                    json.dump(complete_results, f, indent=2, default=str)
            else:
                # Generate HTML report
                self._generate_html_report(complete_results, output_file)
            
            print(f"{Fore.GREEN}[✓] Results saved to {output_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[✗] Failed to save results: {str(e)}{Style.RESET_ALL}")
    
    def _generate_html_report(self, results: Dict, output_file: str):
        """Generate HTML vulnerability report"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vulnerability Scan Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 8px; }
                .critical { color: #dc3545; font-weight: bold; }
                .high { color: #fd7e14; font-weight: bold; }
                .medium { color: #ffc107; font-weight: bold; }
                .low { color: #28a745; font-weight: bold; }
                .vulnerability { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AI-Powered Vulnerability Scan Report</h1>
                <p><strong>Target:</strong> {target_url}</p>
                <p><strong>Scan Date:</strong> {scan_date}</p>
                <p><strong>Total Vulnerabilities:</strong> {total_vulns}</p>
            </div>
            
            <h2>Scan Summary</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Pages Crawled</td><td>{pages_crawled}</td></tr>
                <tr><td>Links Found</td><td>{links_found}</td></tr>
                <tr><td>Forms Found</td><td>{forms_found}</td></tr>
                <tr><td>Critical Issues</td><td class="critical">{critical_count}</td></tr>
                <tr><td>High Issues</td><td class="high">{high_count}</td></tr>
                <tr><td>Medium Issues</td><td class="medium">{medium_count}</td></tr>
                <tr><td>Low Issues</td><td class="low">{low_count}</td></tr>
            </table>
            
            <h2>Vulnerability Details</h2>
            {vulnerability_details}
        </body>
        </html>
        """
        
        # Extract data for template
        scan_meta = results.get('scan_metadata', {})
        crawl_data = results.get('crawl_results', {})
        scan_data = results.get('vulnerability_scan', {})
        
        severity_breakdown = scan_data.get('scan_summary', {}).get('severity_breakdown', {})
        
        vulnerability_details = ""
        for vuln in scan_data.get('results', []):
            severity_class = vuln['severity'].lower()
            vulnerability_details += f"""
            <div class="vulnerability">
                <h3 class="{severity_class}">{vuln['vulnerability_type'].replace('_', ' ').title()} - {vuln['severity']}</h3>
                <p><strong>URL:</strong> {vuln['url']}</p>
                <p><strong>Injection Point:</strong> {vuln['injection_point']}</p>
                <p><strong>Payload:</strong> <code>{vuln['payload']}</code></p>
                <p><strong>Confidence:</strong> {vuln['confidence']:.2f}</p>
                <p><strong>Response Time:</strong> {vuln['response_time']:.2f}s</p>
            </div>
            """
        
        html_content = html_template.format(
            target_url=crawl_data.get('base_url', 'Unknown'),
            scan_date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(scan_meta.get('timestamp', time.time()))),
            total_vulns=scan_data.get('total_vulnerabilities_found', 0),
            pages_crawled=crawl_data.get('visited_pages', 0),
            links_found=crawl_data.get('total_links', 0),
            forms_found=crawl_data.get('total_forms', 0),
            critical_count=severity_breakdown.get('Critical', 0),
            high_count=severity_breakdown.get('High', 0),
            medium_count=severity_breakdown.get('Medium', 0),
            low_count=severity_breakdown.get('Low', 0),
            vulnerability_details=vulnerability_details
        )
        
        with open(output_file, 'w') as f:
            f.write(html_content)
    
    async def run_scan(self, target_url: str, output_file: str = None):
        """Run the complete vulnerability scan"""
        self.print_banner()
        
        try:
            # Step 1: Crawl and extract links/forms
            print(f"{Fore.YELLOW}[*] Starting web crawling...{Style.RESET_ALL}")
            extractor = LinkExtractor(target_url)
            crawl_result = extractor.crawl_website()
            
            # Add interesting endpoints to crawl result
            interesting_endpoints = extractor.get_interesting_endpoints()
            crawl_result['interesting_endpoints'] = interesting_endpoints
            
            self.print_crawl_summary(crawl_result)
            
            # Step 2: AI Analysis
            print(f"{Fore.YELLOW}[*] Running AI analysis...{Style.RESET_ALL}")
            async with VulnerabilityScanner() as scanner:
                ai_analysis = await scanner.llm_manager.analyze_target_with_fallback(crawl_result)
                self.print_ai_analysis(ai_analysis)
                
                # Step 3: Intelligent vulnerability scanning
                print(f"{Fore.YELLOW}[*] Starting intelligent vulnerability scan...{Style.RESET_ALL}")
                scan_results = await scanner.scan_target_intelligently(crawl_result)
                self.print_scan_results(scan_results)
            
            # Step 4: Save results
            if output_file:
                self.save_results(crawl_result, ai_analysis, scan_results, output_file)
            
            # Final summary
            total_vulns = scan_results.get('total_vulnerabilities_found', 0)
            if total_vulns > 0:
                print(f"\n{Fore.RED}[!] SCAN COMPLETE: Found {total_vulns} potential vulnerabilities{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Please manually verify all findings before taking action{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}[✓] SCAN COMPLETE: No vulnerabilities detected{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Scan interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}[✗] Scan failed: {str(e)}{Style.RESET_ALL}")
            logger.exception("Scan failed with exception")

def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Vulnerability Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -u http://example.com
  python main.py -u http://example.com -o report.json
  python main.py -u http://example.com -o report.html --depth 2
  python main.py -u http://example.com --gemini-key YOUR_API_KEY
        """
    )
    
    parser.add_argument('-u', '--url', required=True, help='Target URL to scan')
    parser.add_argument('-o', '--output', help='Output file (JSON or HTML)')
    parser.add_argument('--depth', type=int, help='Maximum crawling depth (default: 3)')
    parser.add_argument('--gemini-key', help='Gemini API key')
    parser.add_argument('--ollama-host', help='Ollama host URL (default: http://localhost:11434)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--no-sql', action='store_true', help='Disable SQL injection testing')
    parser.add_argument('--no-xss', action='store_true', help='Disable XSS testing')
    parser.add_argument('--no-path-traversal', action='store_true', help='Disable path traversal testing')
    parser.add_argument('--no-command-injection', action='store_true', help='Disable command injection testing')
    parser.add_argument('--no-idor', action='store_true', help='Disable IDOR testing')
    
    args = parser.parse_args()
    
    # Update config based on arguments
    if args.depth:
        config.max_depth = args.depth
    if args.gemini_key:
        config.gemini_api_key = args.gemini_key
        os.environ['GEMINI_API_KEY'] = args.gemini_key
    if args.ollama_host:
        config.ollama_host = args.ollama_host
    if args.verbose:
        config.verbose = True
        logging.getLogger().setLevel(logging.INFO)
    
    # Update vulnerability testing flags
    if args.no_sql:
        config.test_sql_injection = False
    if args.no_xss:
        config.test_xss = False
    if args.no_path_traversal:
        config.test_path_traversal = False
    if args.no_command_injection:
        config.test_command_injection = False
    if args.no_idor:
        config.test_idor = False
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print(f"{Fore.RED}[✗] Invalid URL. Must start with http:// or https://{Style.RESET_ALL}")
        sys.exit(1)
    
    # Run the scanner
    cli = VulnScannerCLI()
    try:
        asyncio.run(cli.run_scan(args.url, args.output))
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Scan interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[✗] Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()