import os
from dotenv import load_dotenv
load_dotenv()

try:
    from crewai_tools.tools.serper_dev_tool import SerperDevTool
    search_tool = SerperDevTool()
except ImportError:
    try:
        from crewai_tools import SerperDevTool
        search_tool = SerperDevTool()
    except ImportError:
        search_tool = None

from langchain_community.document_loaders import PyPDFLoader
from crewai.tools import tool

@tool
def read_data_tool(path: str = 'data/sample.pdf') -> str:
    """Tool to read data from a pdf file from a path

    Args:
        path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

    Returns:
        str: Full Financial Document file
    """
    
    docs = PyPDFLoader(file_path=path).load()

    full_report = ""
    for data in docs:
        content = data.page_content
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")
            
        full_report += content + "\n"
        
    return full_report

class FinancialDocumentTool:
    @staticmethod
    def read_data_tool(path='data/sample.pdf'):
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Financial Document file
        """
        
        docs = PyPDFLoader(file_path=path).load()

        full_report = ""
        for data in docs:
            content = data.page_content
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
                
            full_report += content + "\n"
            
        return full_report

class InvestmentTool:
    async def analyze_investment_tool(financial_document_data):
        processed_data = financial_document_data
        
        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1
                
        # TODO: Implement investment analysis logic here
        return "Investment analysis functionality to be implemented"

class RiskTool:
    async def create_risk_assessment_tool(financial_document_data):        
        # TODO: Implement risk assessment logic here
        return "Risk assessment functionality to be implemented"