
from brownie import accounts, web3, Wei, chain
from brownie.network.transaction import TransactionReceipt
from brownie.convert import to_address
import pytest
from brownie import Contract
from settings import *





##############################################
# Token Factory
##############################################

@pytest.fixture(scope='module', autouse=True)
def token_factory(BokkyPooBahsFixedSupplyTokenFactory):

    token_factory = BokkyPooBahsFixedSupplyTokenFactory.deploy({'from': accounts[0]})
    return token_factory



@pytest.fixture(scope='module', autouse=True)
def auction_token(FixedSupplyToken):
    token_owner = accounts[0]
    name = 'BASE TOKEN'
    symbol = 'TKN'
    initial_supply = 10*AUCTION_TOKENS
    auction_token = FixedSupplyToken.deploy({'from': token_owner})
    tx = auction_token.init(token_owner, symbol,name, 18,initial_supply, {'from': token_owner})
    return auction_token

# @pytest.fixture(scope='module', autouse=True)
# def payment_token(token_factory, FixedSupplyToken):
#     token_owner = accounts[0]
#     name = 'PAY TOKEN'
#     symbol = 'PAY'
#     initial_supply = PAYMENT_TOKENS
#     tx = token_factory.deployTokenContract(symbol,name, 18,initial_supply, {'from': token_owner, 'value': '0.2 ethers'})
#     payment_token = FixedSupplyToken.at(tx.return_value)
#     return payment_token

@pytest.fixture(scope='module', autouse=True)
def payment_token(FixedSupplyToken):
    token_owner = accounts[0]
    name = 'PAY TOKEN'
    symbol = 'PAY'
    initial_supply = 10*PAYMENT_TOKENS
    payment_token = FixedSupplyToken.deploy({'from': token_owner})
    tx = payment_token.init(token_owner, symbol,name, 18,initial_supply, {'from': token_owner})
    return payment_token

# ##############################################
# # Auction
# ##############################################


@pytest.fixture(scope='module', autouse=True)
def dutch_auction_template(DutchSwapAuction):
    dutch_auction_template = DutchSwapAuction.deploy({'from': accounts[0]})
    return dutch_auction_template



@pytest.fixture(scope='module', autouse=True)
def auction_factory(DutchSwapFactory, dutch_auction_template):
    auction_factory = DutchSwapFactory.deploy({"from": accounts[0]})
    auction_factory.initDutchSwapFactory(dutch_auction_template, 0, {"from": accounts[0]})
    assert auction_factory.numberOfAuctions( {'from': accounts[0]}) == 0 

    return auction_factory





@pytest.fixture(scope='module', autouse=True)
def dutch_auction(DutchSwapAuction, auction_token):
    
    startDate = chain.time() +10
    endDate = startDate + AUCTION_TIME
    wallet = accounts[1]
    funder = accounts[0]

    dutch_auction = DutchSwapAuction.deploy({'from': accounts[0]})
    tx = auction_token.approve(dutch_auction, AUCTION_TOKENS, {'from':funder})

    dutch_auction.initDutchAuction(funder, auction_token, AUCTION_TOKENS, startDate, endDate,ETH_ADDRESS, AUCTION_START_PRICE, AUCTION_RESERVE, wallet, {"from": accounts[0]})
    assert dutch_auction.clearingPrice( {'from': accounts[0]}) == AUCTION_START_PRICE

    # Cannot contribute early
    # with reverts():
    #     tx = token_buyer.transfer(dutch_auction, eth_to_transfer)

    # testing pre auction calcs
    assert dutch_auction.calculateCommitment(0) == 0 
    assert dutch_auction.calculateCommitment(AUCTION_START_PRICE) == AUCTION_START_PRICE
    assert dutch_auction.calculateCommitment(AUCTION_START_PRICE*AUCTION_TOKENS / TENPOW18) == AUCTION_START_PRICE*AUCTION_TOKENS / TENPOW18
    assert dutch_auction.calculateCommitment(10 * AUCTION_START_PRICE*AUCTION_TOKENS ) == AUCTION_START_PRICE*AUCTION_TOKENS / TENPOW18

    # Move the chain to the moment the auction begins
    chain.sleep(10)
    return dutch_auction



@pytest.fixture(scope='module', autouse=True)
def erc20_auction(DutchSwapAuction, auction_token, payment_token):
    startDate = chain.time() +10
    endDate = startDate + AUCTION_TIME
    wallet = accounts[1]
    funder = accounts[0]

    erc20_auction = DutchSwapAuction.deploy({'from': accounts[0]})
    tx = auction_token.approve(erc20_auction, AUCTION_TOKENS, {'from':funder})

    erc20_auction.initDutchAuction(funder, auction_token, AUCTION_TOKENS, startDate, endDate,payment_token, AUCTION_START_PRICE, AUCTION_RESERVE, wallet, {"from": accounts[0]})
    assert erc20_auction.clearingPrice( {'from': accounts[0]}) == AUCTION_START_PRICE

    # with reverts():
    #     tx = token_buyer.transfer(dutch_auction, eth_to_transfer)

    chain.sleep(10)
    return erc20_auction



# Skipped for code coverage
# Factory tested seperately for coverage

# @pytest.fixture(scope='module', autouse=True)
# def factory_token(token_factory, FixedSupplyToken):
#     token_owner = accounts[0]
#     name = 'FACTORY TOKEN'
#     symbol = 'FACT'
#     initial_supply = 10*AUCTION_TOKENS
#     tx = token_factory.deployTokenContract(symbol,name, 18,initial_supply, {'from': token_owner, 'value': '0.2 ethers'})
#     factory_token = FixedSupplyToken.at(tx.return_value)
#     return factory_token


# @pytest.fixture(scope='module', autouse=True)
# def dutch_auction(DutchSwapAuction, auction_factory, auction_token):
#     startDate = chain.time() +10
#     endDate = startDate + AUCTION_TIME
#     wallet = accounts[1]
#     tx = auction_token.approve(auction_factory, AUCTION_TOKENS, {'from': accounts[0]})
#     tx = auction_factory.deployDutchAuction(auction_token, AUCTION_TOKENS, startDate, endDate,ETH_ADDRESS, AUCTION_START_PRICE, AUCTION_RESERVE, wallet, {"from": accounts[0]})
#     dutch_auction = DutchSwapAuction.at(tx.return_value)
#     assert dutch_auction.clearingPrice() == AUCTION_START_PRICE
#     chain.sleep(10)
#     return dutch_auction


# @pytest.fixture(scope='module', autouse=True)
# def erc20_auction(DutchSwapAuction, auction_factory, auction_token, payment_token):
#     startDate = chain.time() +10
#     endDate = startDate + AUCTION_TIME
#     wallet = accounts[1]
    
#     tx = auction_token.approve(auction_factory, AUCTION_TOKENS, {'from': accounts[0]})
#     tx = auction_factory.deployDutchAuction(auction_token, AUCTION_TOKENS, startDate, endDate,payment_token, AUCTION_START_PRICE, AUCTION_RESERVE, wallet, {"from": accounts[0]})
#     erc20_auction = DutchSwapAuction.at(tx.return_value)
#     assert erc20_auction.clearingPrice() == AUCTION_START_PRICE
#     chain.sleep(10)
#     return erc20_auction
