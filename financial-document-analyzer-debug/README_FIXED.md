# Financial Document Analyzer - Fixed Version

A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered agents with CrewAI framework.

## Project Overview

This system leverages multiple AI agents working collaboratively to:
- Verify financial documents for authenticity and completeness
- Analyze financial statements and extract key metrics
- Provide data-driven investment recommendations
- Conduct comprehensive risk assessments
- Answer specific financial inquiries

## Bugs Found and Fixed

### 1. **tools.py - Multiple Critical Issues**

#### Bug 1.1: Undefined Import
- **Issue**: `from crewai_tools import tools` - incorrect import, `tools` doesn't exist as a module export
- **Fix**: Changed to `from crewai_tools import tool` (decorator)

#### Bug 1.2: Missing Dependency Import
- **Issue**: `Pdf(file_path=path)` referenced but never imported
- **Fix**: Added `from langchain_community.document_loaders import PyPDFLoader`

#### Bug 1.3: Incorrect Method Definition
- **Issue**: `async def read_data_tool(path='data/sample.pdf'):` - async without proper class structure
- **Fix**: Converted to `@staticmethod` and `@tool` decorated function for crewai compatibility

#### Bug 1.4: Class Instantiation Error
- **Issue**: Class defined with empty parentheses `class FinancialDocumentTool():` but methods weren't callable
- **Fix**: Made `read_data_tool` a static method with proper decorators

#### Bug 1.5: Wrong PDF Loader
- **Issue**: Used undefined `Pdf` class
- **Fix**: Changed to `PyPDFLoader` from `langchain_community`

### 2. **agents.py - Initialization and Prompt Issues**

#### Bug 2.1: Circular LLM Definition
- **Issue**: `llm = llm` - circular self-reference, LLM never actually initialized
- **Fix**: Changed to `llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)`

#### Bug 2.2: Missing LLM Import
- **Issue**: Used `llm` but never imported `ChatOpenAI`
- **Fix**: Added `from langchain_openai import ChatOpenAI`

#### Bug 2.3: Incorrect Import
- **Issue**: `from crewai.agents import Agent` - wrong import path
- **Fix**: Changed to `from crewai import Agent`

#### Bug 2.4: Tool Parameter Syntax Error
- **Issue**: `tool=[FinancialDocumentTool.read_data_tool]` - singular parameter with wrong reference
- **Fix**: Changed to `tools=[FinancialDocumentTool.read_data_tool()]` (plural, instantiated)

#### Bug 2.5: Unprofessional Agent Prompts (All Agents)
- **Issue**: All agent backstories and goals were designed to produce unreliable outputs:
  - Encouraged hallucination and making up data
  - Suggested ignoring compliance regulations
  - Promoted unethical investment advice
  - Discouraged careful document analysis
- **Fix**: Replaced with professional, accurate prompts focusing on:
  - Data-driven analysis
  - Regulatory compliance
  - Transparent risk disclosure
  - Factual recommendations

### 3. **task.py - Task Description Corruption**

#### Bug 3.1: Hallucination-Promoting Prompts (All Tasks)
- **Issue**: Task descriptions explicitly encouraged:
  - Making up information not in the documents
  - Creating fake URLs and sources
  - Contradicting findings within same response
  - Ignoring user queries
  - Inventing non-existent financial models
- **Fix**: Replaced with professional task descriptions requiring:
  - Evidence-based analysis
  - Clear documentation of findings
  - Proper disclosure of assumptions
  - Adherence to user queries
  - Realistic recommendations

#### Bug 3.2: Incorrect Tool References
- **Issue**: `tools=[FinancialDocumentTool.read_data_tool]` - not instantiated
- **Fix**: Changed to `tools=[FinancialDocumentTool.read_data_tool()]`

#### Bug 3.3: Missing Agent Imports
- **Issue**: `investment_analysis` task used `financial_analyst` agent, but investment advice wasn't specialized
- **Fix**: Updated to use `investment_advisor` agent for investment tasks and `risk_assessor` for risk tasks

### 4. **main.py - Function Naming and Context Issues**

#### Bug 4.1: Function Name Shadowing
- **Issue**: `async def analyze_financial_document()` shadowed the imported task with the same name
- **Fix**: Renamed endpoint function to `analyze_document()`

#### Bug 4.2: Unused Function Parameter
- **Issue**: `run_crew()` accepted `file_path` parameter but never passed it to the crew
- **Fix**: Added `file_path` to the context dictionary passed to `crew.kickoff()`

#### Bug 4.3: Incomplete Agent/Task Configuration
- **Issue**: Only `financial_analyst` and one task were included in the crew
- **Fix**: Added all agents and tasks:
  - `verifier` - document verification
  - `financial_analyst` - financial analysis
  - `investment_advisor` - investment recommendations
  - `risk_assessor` - risk analysis

#### Bug 4.4: Improper Query Validation
- **Issue**: `if query=="" or query is None:` - redundant condition
- **Fix**: Changed to `if not query or query == "":` - cleaner logic

### 5. **requirements.txt - Missing Dependencies**

#### Bug 5.1: Incomplete Dependencies
- **Issue**: Missing critical packages:
  - `langchain-community` (for PyPDFLoader)
  - `python-dotenv` (for .env file loading)
  - `pypdf` (PDF handling)
  - `uvicorn` (ASGI server)
- **Fix**: Added all missing dependencies with appropriate versions

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip package manager
- OpenAI API key

### Installation

1. **Clone/Download the project**
   ```bash
   cd financial-document-analyzer
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   SERPER_API_KEY=your_serper_api_key_here  # Optional, for web search
   ```

### Running the Application

#### Using FastAPI with Uvicorn
```bash
python main.py
```

The API will be available at `http://localhost:8000`

#### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check
```
GET /
```
**Response**:
```json
{
  "message": "Financial Document Analyzer API is running"
}
```

### 2. Analyze Financial Document
```
POST /analyze
```

**Parameters**:
- `file` (UploadFile, required): PDF file containing financial document
- `query` (string, optional): Specific question or analysis request

**Example Request**:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@financial_statement.pdf" \
  -F "query=What is the company's debt-to-equity ratio and is it healthy?"
```

**Response**:
```json
{
  "status": "success",
  "query": "What is the company's debt-to-equity ratio and is it healthy?",
  "analysis": "Comprehensive analysis output from all agents...",
  "file_processed": "financial_statement.pdf"
}
```

## System Architecture

### Agents

1. **Document Verification Specialist** (`verifier`)
   - Validates document authenticity
   - Assesses completeness of financial statements
   - Identifies data quality issues
   - Flags missing sections

2. **Senior Financial Analyst** (`financial_analyst`)
   - Extracts key financial metrics
   - Performs ratio analysis
   - Identifies trends and patterns
   - Answers specific financial questions

3. **Investment Strategy Advisor** (`investment_advisor`)
   - Develops investment recommendations
   - Considers company financial health
   - Addresses risk tolerance
   - Discloses conflicts of interest

4. **Risk Assessment Specialist** (`risk_assessor`)
   - Identifies financial risks
   - Evaluates operational risks
   - Analyzes market risks
   - Proposes mitigation strategies

### Workflow

```
User submits financial document + query
        ↓
Document Verification (validates document)
        ↓
Financial Analysis (analyzes metrics & answers query)
        ↓
Investment Analysis (develops recommendations)
        ↓
Risk Assessment (identifies risks & mitigations)
        ↓
Comprehensive report returned to user
```

## File Structure

```
financial-document-analyzer/
├── main.py                 # FastAPI application and endpoints
├── agents.py              # AI agents configuration
├── task.py                # Task definitions
├── tools.py               # Tool implementations
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── data/                  # Uploaded documents storage
├── outputs/               # Analysis results storage
└── README.md              # This file
```

## Configuration

### Model Configuration
Currently using `gpt-4-turbo` for the LLM. To change:

Edit `agents.py`:
```python
llm = ChatOpenAI(model="gpt-4", temperature=0.7)  # Or other models
```

### Agent Configuration
Adjust agent behavior by modifying in `agents.py`:
- `temperature`: Controls randomness (0 = deterministic, 1 = random)
- `max_iter`: Maximum iterations per agent
- `memory`: Enable/disable agent memory

## Features

✅ **Professional Financial Analysis**
- Accurate extraction of financial metrics
- Evidence-based recommendations
- Compliance with financial standards

✅ **Comprehensive Risk Assessment**
- Identification of financial risks
- Stress testing and scenario analysis
- Practical mitigation strategies

✅ **Multi-Agent Collaboration**
- Specialized agents working together
- Cross-validation of analysis
- Comprehensive coverage

✅ **API Integration Ready**
- RESTful API design
- Easy integration with other systems
- Comprehensive error handling

## Usage Examples

### Example 1: Income Statement Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@quarterly_report.pdf" \
  -F "query=Analyze the revenue growth and margin trends"
```

### Example 2: Risk Assessment Request
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@annual_report.pdf" \
  -F "query=What are the main risks to this company and how can they be mitigated?"
```

### Example 3: Investment Recommendation
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@balance_sheet.pdf" \
  -F "query=Is this company a good investment opportunity? Why or why not?"
```

## Troubleshooting

### OpenAI API Key Not Found
**Error**: `AuthenticationError: API key not found`
**Solution**: Ensure `.env` file has `OPENAI_API_KEY=your_key` and file is in project root

### PDF Processing Fails
**Error**: `FileNotFoundError: No such file or directory`
**Solution**: Ensure `data/` directory exists or manually create it

### Agent Timeout
**Error**: `Timeout waiting for agent response`
**Solution**: Increase `max_iter` in agent configuration or use simpler queries

### Import Errors
**Error**: `ModuleNotFoundError: No module named 'langchain_community'`
**Solution**: Run `pip install -r requirements.txt` again to ensure all dependencies

## Best Practices

1. **Document Quality**: Use clear, complete financial documents for best results
2. **Query Specificity**: Ask specific questions for more focused analysis
3. **File Management**: The system auto-cleans temporary files; no manual cleanup needed
4. **API Rate Limits**: Be mindful of OpenAI API rate limits and costs
5. **Error Handling**: Check API response status before processing results

## Future Enhancements

Potential improvements for future versions:
- Database integration for analysis history
- Caching mechanism for frequent documents
- Advanced visualization of financial metrics
- Support for multiple document formats (Excel, JSON)
- Batch processing capabilities
- User authentication and authorization

## License

This project is provided as-is for educational and professional purposes.

## Support

For issues or questions, review the troubleshooting section or check API documentation at `/docs` endpoint.

---

**Last Updated**: February 2026
**Status**: All bugs fixed and fully functional
