# AI-Powered Vulnerability Scanner

An intelligent web application vulnerability scanner that uses AI (Gemini and Ollama) to intelligently analyze targets, generate custom payloads, and detect security vulnerabilities.

## Features

🤖 **AI-Powered Analysis**: Uses Gemini API and Ollama models to intelligently analyze targets and generate context-specific payloads

🕸️ **Smart Web Crawling**: Automatically discovers internal links and forms with depth-based crawling

🎯 **Targeted Testing**: AI decides which endpoints to prioritize and what vulnerability types to test

🔍 **Multiple Vulnerability Types**:
- SQL Injection
- Cross-Site Scripting (XSS)
- Path Traversal
- Command Injection
- Insecure Direct Object References (IDOR)

📊 **Beautiful Reporting**: Console output with colors, tables, and HTML/JSON reports

🔧 **Highly Configurable**: Extensive configuration options for scan depth, AI models, and testing parameters

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ai-vulnerability-scanner
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment** (optional):
```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

## Configuration

### AI Models

#### Gemini API (Recommended)
1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the API key:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

#### Ollama (Local AI)
1. Install [Ollama](https://ollama.ai/)
2. Pull a model:
```bash
ollama pull llama2
```
3. Start Ollama server:
```bash
ollama serve
```

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key
OLLAMA_HOST=http://localhost:11434
GEMINI_MODEL=gemini-pro
OLLAMA_MODEL=llama2

# Scanner Settings
MAX_DEPTH=3
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30

# Vulnerability Testing
TEST_SQL_INJECTION=true
TEST_XSS=true
TEST_PATH_TRAVERSAL=true
TEST_COMMAND_INJECTION=true
TEST_IDOR=true
```

## Usage

### Basic Usage

```bash
# Basic scan
python main.py -u http://example.com

# Scan with output file
python main.py -u http://example.com -o report.json

# HTML report
python main.py -u http://example.com -o report.html

# Custom depth and verbose output
python main.py -u http://example.com --depth 2 --verbose
```

### Advanced Usage

```bash
# Using specific Gemini API key
python main.py -u http://example.com --gemini-key YOUR_API_KEY

# Custom Ollama host
python main.py -u http://example.com --ollama-host http://192.168.1.100:11434

# Disable specific vulnerability tests
python main.py -u http://example.com --no-sql --no-xss

# Combination of options
python main.py -u http://example.com -o detailed_report.html --depth 3 --verbose --gemini-key YOUR_KEY
```

### Command Line Options

```
-u, --url              Target URL to scan (required)
-o, --output           Output file (JSON or HTML)
--depth               Maximum crawling depth (default: 3)
--gemini-key          Gemini API key
--ollama-host         Ollama host URL (default: http://localhost:11434)
--verbose             Enable verbose logging
--no-sql              Disable SQL injection testing
--no-xss              Disable XSS testing
--no-path-traversal   Disable path traversal testing
--no-command-injection Disable command injection testing
--no-idor             Disable IDOR testing
```

## How It Works

### 1. Web Crawling
- Discovers internal links and forms
- Analyzes page structure and identifies interesting endpoints
- Respects depth limits and rate limiting

### 2. AI Analysis
- Sends discovered endpoints and forms to AI models
- AI analyzes the target and provides:
  - Priority endpoints to test
  - Recommended vulnerability types for each endpoint
  - Risk assessment for forms
  - Testing strategy recommendations

### 3. Intelligent Testing
- Generates context-specific payloads using AI
- Tests multiple injection points:
  - Query parameters
  - Form fields
  - URL paths
  - HTTP headers
- Analyzes responses for vulnerability indicators

### 4. Reporting
- Real-time console output with colors and progress
- Detailed vulnerability reports
- JSON and HTML export options

## Example Output

```
╔══════════════════════════════════════════════════════════════════╗
║                    AI-Powered Vulnerability Scanner             ║
║                           Version 1.0                           ║
╚══════════════════════════════════════════════════════════════════╝

[*] Initializing AI-powered vulnerability scanner...
[✓] Configuration loaded
[✓] Available AI models: gemini, ollama
[✓] Gemini API configured

[*] Starting web crawling...

============================================================
            CRAWLING SUMMARY
============================================================
Target URL: http://example.com
Pages Visited: 15
Links Found: 47
Forms Found: 3

[*] Interesting endpoints found:
  • http://example.com/admin (admin_endpoint)
  • http://example.com/login (admin_endpoint)
  • http://example.com/api/users (api_endpoint)

[*] Running AI analysis...

============================================================
            AI ANALYSIS RESULTS
============================================================

[*] High Priority Targets:
+------------------+----------+---------------------+------------------------+
| URL              | Priority | Vulnerability Types | Reasoning              |
+==================+==========+=====================+========================+
| /admin           | 9/10     | sql_injection, xss  | Admin interface with   |
|                  |          |                     | high privilege access |
+------------------+----------+---------------------+------------------------+

[*] Starting intelligent vulnerability scan...

VULNERABILITY FOUND: sql_injection in http://example.com/login
Payload: ' OR '1'='1
Confidence: 0.85

============================================================
            VULNERABILITY SCAN RESULTS
============================================================

[!] Found 2 potential vulnerabilities

[*] Vulnerabilities by Type:
  • Sql Injection: 1
  • Xss: 1

[*] Severity Breakdown:
  • Critical: 1
  • Medium: 1

[!] SCAN COMPLETE: Found 2 potential vulnerabilities
[!] Please manually verify all findings before taking action
```

## Security Considerations

⚠️ **Important**: This tool is for authorized security testing only.

- **Only test applications you own or have explicit permission to test**
- **Payloads are designed to be non-destructive**
- **Always verify findings manually before reporting**
- **Follow responsible disclosure practices**
- **Respect rate limits and target server resources**

## Legal Disclaimer

This tool is intended for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before scanning any targets. The developers are not responsible for any misuse or damage caused by this tool.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**"No LLM clients available"**
- Ensure you have either a Gemini API key set or Ollama running
- Check your internet connection for Gemini API
- Verify Ollama is accessible at the configured host

**"Gemini API error"**
- Verify your API key is correct
- Check your API quota/billing status
- Ensure you're using a supported model

**"Ollama connection failed"**
- Ensure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Verify the host URL is correct

**Slow scanning**
- Reduce crawling depth with `--depth`
- Limit concurrent requests in config
- Use specific vulnerability tests to reduce scope

### Debug Mode

Enable verbose logging for detailed debugging:
```bash
python main.py -u http://example.com --verbose
```

Check the log file for detailed information:
```bash
tail -f vulnerability_scan.log
```

## Roadmap

- [ ] Support for more vulnerability types (XXE, CSRF, etc.)
- [ ] Integration with additional AI models (Claude, GPT-4, etc.)
- [ ] Web interface for easier usage
- [ ] Plugin system for custom vulnerability checks
- [ ] Integration with popular security tools
- [ ] Advanced payload encoding/obfuscation
- [ ] Machine learning for false positive reduction
