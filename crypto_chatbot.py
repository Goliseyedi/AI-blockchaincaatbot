from flask import Flask, request, render_template, redirect, url_for
import openai 
import os
import sys
import boto3
import uuid
import time
from datetime import datetime

def is_crypto_related(query):
    
    crypto_keywords = [
       
    'cryptocurrency', 'blockchain', 'bitcoin', 'ethereum', 'crypto', 'ledger', 
    'token', 'coin', 'wallet', 'altcoin', 'litecoin', 'ripple', 'xrp', 'dogecoin', 
    'smart contract', 'defi', 'decentralized finance', 'nft', 'non-fungible token', 
    'btc', 'eth', 'block explorer', 'mining', 'hash rate', 'proof of work', 
    'proof of stake', 'ethereum 2.0', 'staking', 'cryptography', 'private key', 
    'public key', 'satoshi nakamoto', 'gas fees', 'erc20', 'erc721', 'dapp', 
    'decentralized application', 'chainlink', 'polkadot', 'cardano', 'ada', 
    'binance', 'bnb', 'exchange', 'crypto exchange', 'digital currency', 
    'block height', 'consensus algorithm', 'cold storage', 'hot wallet', 
    'uniswap', 'pancakeswap', 'yield farming', 'liquidity pool', 'chain split', 
    'fork', 'soft fork', 'hard fork', 'halving', 'segwit', 'lightning network', 
    'scalability', 'sharding', 'layer 2', 'sidechain', 'cross-chain', 'atomic swap', 
    'oracle', 'stablecoin', 'tether', 'usdt', 'usdc', 'makerdao', 'dai', 
    'wrapped bitcoin', 'wbtc', 'zcash', 'monero', 'privacy coin', 'aml', 
    'kyc', 'anti-money laundering', 'know your customer', 'ledger nano', 'trezor', 
    'hardware wallet', 'paper wallet', 'fiat to crypto', 'crypto to fiat', 
    'satoshi', 'vitalik buterin', 'smart contract audit', 'gwei', 'sat', 'decentralization'
]

    
    return any(keyword in query.lower() for keyword in crypto_keywords)

def is_financial_advice(query):
    
    financial_advice_keywords = [
    'invest', 'investment', 'buy', 'sell', 'trade', 'trading', 'portfolio',
    'profit', 'loss', 'risk', 'return', 'roi', 'return on investment',
    'financial advice', 'should I', 'is it good to', 'is it safe to',
    'market prediction', 'price prediction', 'forecast', 'money', 'capital',
    'asset allocation', 'diversification', 'savings', 'stock market',
    'shares', 'equity', 'bond', 'securities', 'mutual fund', 'index fund',
    'hedge fund', 'pension', 'retirement', '401k', 'IRA', 'broker',
    'trader', 'financial planner', 'wealth management', 'tax', 'insurance',
    'real estate', 'commodity', 'gold', 'silver', 'precious metal',
    'cryptocurrency investment', 'bitcoin investment', 'ethereum investment',
    'crypto trading', 'day trading', 'swing trading', 'margin trading',
    'leverage', 'bull market', 'bear market', 'market analysis',
    'technical analysis', 'fundamental analysis', 'portfolio management',
    'asset management', 'futures', 'options', 'derivatives', 'short selling',
    'long position', 'short position', 'dividend', 'yield', 'credit score',
    'loan', 'debt', 'bankruptcy', 'inflation', 'deflation', 'liquidity',
    'volatility', 'fiscal policy', 'monetary policy', 'economy', 'recession',
    'depression', 'trading platform', 'exchange rate', 'currency',
    'forex', 'fx trading', 'financial market', 'capital market', 'money market',
    'saving account', 'interest rate', 'APR', 'annual percentage rate',
    'credit card', 'mortgage', 'refinance', 'budget', 'financial goal',
    'financial risk', 'investment strategy', 'risk tolerance', 
    'financial regulation', 'compliance', 'KYC', 'AML', 'due diligence'
]

    return any(keyword in query.lower() for keyword in financial_advice_keywords)

def is_tech_explanation_query(query):
    tech_explanation_keywords = [
    'how does', 'explain', 'what is', 'mechanism', 'technology behind',
    'working of', 'functioning of', 'underlying technology', 'tech stack',
    'architecture', 'blockchain design', 'consensus mechanism', 'smart contract logic',
    'blockchain protocol', 'distributed ledger', 'hash function', 'encryption',
    'decentralized', 'peer-to-peer', 'P2P network', 'cryptography', 'proof of work',
    'proof of stake', 'mining algorithm', 'block validation', 'node operation',
    'block creation', 'transaction processing', 'ledger synchronization',
    'cryptographic signature', 'digital signature', 'public-private key',
    'merkle tree', 'dapp architecture', 'gas computation', 'scalability solutions',
    'layer 1', 'layer 2', 'sidechains', 'plasma', 'rollups', 'sharding',
    'interoperability', 'cross-chain communication', 'atomic cross-chain trading',
    'consensus algorithm', 'PoW', 'PoS', 'DPoS', 'Delegated Proof of Stake',
    'Byzantine Fault Tolerance', 'BFT', 'PBFT', 'Practical Byzantine Fault Tolerance',
    'zero-knowledge proofs', 'ZKP', 'snarks', 'starks', 'off-chain computation',
    'on-chain governance', 'tokenomics', 'token economics', 'network nodes',
    'node consensus', 'staking mechanisms', 'validator nodes', 'crypto economics',
    'hashing algorithm', '51% attack', 'sybil attack', 'double spend problem',
    'smart contract deployment', 'oracle integration', 'data privacy', 
    'blockchain scalability', 'layer-0', 'cross-layer optimization', 'inter-chain bridges',
    'state channels', 'payment channels', 'cryptocurrency forks', 'hard fork', 'soft fork'
]

    return any(keyword in query.lower() for keyword in tech_explanation_keywords)

def get_openai_response(query, context=""):

    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    full_prompt = context + query  

    try:
        response = openai.Completion.create(                       
          model="text-davinci-003",
          prompt=full_prompt,
          temperature=0.7,
          max_tokens=250
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
glossary_table = dynamodb.Table('GlossaryData')                                     # type: ignore
feedback_table = dynamodb.Table('UserFeedback')                                       # type: ignore

def lookup_term(term):
    try:
        response = glossary_table.get_item(Key={'term': term.lower()})
        item = response.get('Item')
        if item:
            return f"Glossary :\n{item['definition']}"
        else:
            return "Term not found in the glossary."
    except Exception as e:
        print(f"Error fetching term from DynamoDB: {e}")
        return f"An error occurred while looking up the term: {e}"

def chatbot(query):
    normalized_query = query.lower().strip()
    definition = lookup_term(normalized_query)
    return definition

def summarize_whitepaper(whitepaper_text):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")

    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="Summarize this text in one sentence:\n\n" + whitepaper_text,
        temperature=0.3,
        max_tokens=60,  
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    summary = response.choices[0].text.strip()

    desired_length = 80 
    if len(summary) > desired_length:
        summary = summary[:desired_length] + '...'

    return summary

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    warning = None
    summary_response = None
    if request.method == 'POST':
        user_input = request.form['query']
        if "summarize" in user_input.lower():
            summary_response = summarize_whitepaper(user_input)
            return render_template('index.html', summary_response=summary_response)
        if is_financial_advice(user_input) and not is_tech_explanation_query(user_input):
            warning = "Please note that the information provided here is not financial advice."
        elif is_crypto_related(user_input) or is_tech_explanation_query(user_input):
            response = get_openai_response(user_input)
        else:
            warning = "This query does not appear to be related to cryptocurrency or blockchain."
        glossary_response = chatbot(user_input)
        if glossary_response != "Term not found in the glossary.":
            response = glossary_response
        elif is_financial_advice(user_input):
            warning = "Please note that the information provided here is not financial advice."
        elif is_crypto_related(user_input):
            if is_tech_explanation_query(user_input):
                tech_context = "Please explain the technology behind this blockchain project: "
                response = get_openai_response(user_input, tech_context)
            else:
                response = get_openai_response(user_input)
        else:
            warning = "This query does not appear to be related to cryptocurrency or blockchain."
    return render_template('index.html', response=response, warning=warning, summary_response=summary_response)  

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    summary_response = None

    if request.method == 'POST':
        whitepaper_text = request.form['whitepaper_text']
        summary_response = summarize_whitepaper(whitepaper_text)

    return render_template('summarize.html', summary_response=summary_response)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        try:
           
            feedback_id = str(uuid.uuid4())
            rating = request.form['rating']
            comments = request.form['comments']
            timestamp = int(time.mktime(datetime.now().timetuple()))
            feedback_table.put_item(
                Item={
                    'FeedbackID': feedback_id,
                    'Rating': rating,
                    'Comments': comments,
                    'Timestamp': timestamp,
                }
            )
        except Exception as e:
            return "An error occurred: " + str(e)
    return render_template('feedback_form.html')

if __name__ == "__main__":
    app.run(debug=True)
