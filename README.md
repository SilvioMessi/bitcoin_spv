# bitcoin_spv #

## In a nutshell ##
A naïve implementation of Bitcoin Simplified Payment Verification using bloom filters.

This project helped me to gain a better understanding of bitcoin technology.

## Useful documents ##

* [BIP 37](https://github.com/bitcoin/bips/blob/master/bip-0037.mediawiki) 
* [Bitcoin protocol documentation](https://en.bitcoin.it/wiki/Protocol_documentation)

## Dependencies ##

I struggled a lot to find a complete python library for Bitcoin (if you know one let me know ;)). 

In this project a [fork](https://github.com/SilvioMessi/python-bitcoinlib) of the library [python-bitcoinlib](https://github.com/petertodd/python-bitcoinlib) is used. I created the fork in order to improve the support to bloom filters and merkle blocks.

## Features ##
* Client to download the Bitcoin block chain (only headers)
* Client to analyze the Bitcoin block chain, using SPV and bloom filters, in order to find your transactions

__NOTE__: Probably you will have to customize the code used for import the private key if you have exported the key from a wallet different from Bitcoin Core (0.16.0). Please refer at the extensive comment in the file data_store/keys.py.

This is not a Bitcoin wallet! You can use the transactions found to create your own wallet.

## Getting Started ##

* ``` $ git clone https://github.com/SilvioMessi/bitcoin_spv.git ```
* ``` $ cd bitcoin_svp/ ```
* ``` $ virtualenv -p /path/to/python3.6 ENV ```
* ``` $ source ENV/bin/activate ```
* ``` (ENV)$ pip install -r requirements.txt ```
* ``` (ENV)$ python __main__.py ```

### Output example ###
```
Loaded 519145 block headers from data store. Starting the synchronization...
1 block headers downloaded
Synchronization ended! There are 519146 blocks in the bitcoin block chain

Insert private key (WIF-compressed format):L4R6FHtS46R45s2126cUji5P3MN4REagZYqwPtzQNkG2YCqfN1HK

Starting the analysis of the block chain in order to find your transactions...
Transaction ID 14c24561e2c598e70629738315e023ed091e443a78a24d5367b8d80694062723
You earned 14400 bitcoin
----------------------------------------------------------------------------------------------------
Transaction ID 341de47b8c80289378fa444c72af76a6d25705d53445ac3042b87316d587c6d4
You spent the bitcoin earned from transaction with ID
14c24561e2c598e70629738315e023ed091e443a78a24d5367b8d80694062723 (vout index 1)
----------------------------------------------------------------------------------------------------
5000 blocks analyzed
312 blocks analyzed
Analysis ended!
``` 
