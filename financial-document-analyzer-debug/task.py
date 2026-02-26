from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import read_data_tool

analyze_financial_document = Task(
    description="Analyze the provided financial document to address the user's inquiry: {query}\n\
Carefully read and extract key financial metrics, ratios, and data from the document.\n\
Provide a comprehensive analysis that addresses the specific question posed.\n\
Include relevant financial indicators, trends, and context necessary to answer the query.\n\
Ensure all statements are based on information found in the actual financial document.",

    expected_output="""Provide a detailed analysis including:
- Key financial metrics and ratios extracted from the document
- Clear explanation of findings relevant to the user's query
- Supporting data and calculations from the financial statements
- Proper context for interpreting the information
- Any limitations or caveats in the analysis
- Recommendations based on the analysis""",

    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)

investment_analysis = Task(
    description="Based on the financial analysis provided, develop investment recommendations aligned with the company's financial position.\n\
User query: {query}\n\
Analyze the company's financial health, growth prospects, and competitive positioning.\n\
Consider industry trends and market conditions in your recommendations.\n\
Provide investment advice that is suitable to the financial profile demonstrated.\n\
Clearly disclose assumptions and risks underlying any recommendations.",

    expected_output="""Provide investment analysis including:
- Assessment of the company's investment potential
- Key strengths and weaknesses affecting investment attractiveness
- Relevant market and industry context
- Investment recommendations with clear rationale
- Risk factors and potential downside scenarios
- Time horizons and appropriate investor profiles for the investment""",

    agent=investment_advisor,
    tools=[read_data_tool],
    async_execution=False,
)

risk_assessment = Task(
    description="Conduct a comprehensive risk assessment based on the financial document analysis.\n\
User query: {query}\n\
Identify financial risks, operational risks, and market risks evident from the financial statements.\n\
Evaluate historical volatility and potential stress scenarios.\n\
Propose appropriate hedging and mitigation strategies.\n\
Assess the organization's risk management capabilities and gaps.",

    expected_output="""Provide comprehensive risk assessment including:
- Key financial, operational, and market risks identified
- Quantitative measures of exposure where available
- Stress test scenarios and potential impacts
- Risk mitigation strategies and hedging approaches
- Assessment of existing risk management controls
- Recommendations for improving risk resilience
- Clear disclosure of assessment limitations""",

    agent=risk_assessor,
    tools=[read_data_tool],
    async_execution=False,
)

verification = Task(
    description="Verify that the provided document is a legitimate financial document and assess its quality for analysis.\n\
Confirm the document type, issuer, and reporting period.\n\
Check for completeness of required financial statements.\n\
Identify any data quality issues or missing information.\n\
Assess the reliability of the data for investment analysis purposes.",

    expected_output="""Provide verification report including:
- Confirmation of document type and authenticity
- Assessment of completeness (presence of all required statements)
- Data quality evaluation and any inconsistencies noted
- Identification of missing or incomplete sections
- Overall reliability assessment for analysis purposes
- Any limitations that may affect analysis conclusions
- Recommendations for addressing identified issues""",

    agent=verifier,
    tools=[read_data_tool],
    async_execution=False
)