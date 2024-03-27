from flask import Flask, request, jsonify
from web3 import Web3
import google.generativeai as genai


application = Flask(__name__)

ganache_url = "http://192.168.29.128:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

target_address = web3.to_checksum_address('0x439A9320469aFC5f078722a1bbBbb0c86e83F328')
abi = '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"_txHash","type":"bytes32"},{"internalType":"address","name":"_sender","type":"address"},{"internalType":"address","name":"_receiver","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_date","type":"string"}],"name":"addTransaction","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getAllTransactions","outputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"date","type":"string"}],"internalType":"struct UserRegistry.Transaction[]","name":"","type":"tuple[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"getAllTransactionsForAccount","outputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"date","type":"string"}],"internalType":"struct UserRegistry.Transaction[]","name":"","type":"tuple[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"_txHash","type":"bytes32"}],"name":"getTransactionName","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"_userAddress","type":"address"}],"name":"getUserDetails","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"_txHash","type":"bytes32"},{"internalType":"string","name":"_name","type":"string"}],"name":"setTransactionName","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_userAddress","type":"address"},{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_image","type":"string"}],"name":"setUserDetails","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"transactionKeys","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"transactionNames","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"transactions","outputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"date","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"userImages","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"userNames","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]'
target = web3.eth.contract(address= target_address, abi = abi)

master_address = "0x7289547324780bd15B6293F0b2e61FD9CEDd5f2C"
master_key = "0xaef033fd5eb0b7fd8d9ff45e78ba4f1ee5913c0262d649cc39aad6a2152df522"

@application.route('/transaction', methods=['POST'])
def transaction():
    try:
        acc1 = request.form['acc1']
        p1 = request.form['p1']
        acc2 = request.form['acc2']
        eth = request.form['eth']
        tx_name = request.form['tx_name']
        date = request.form['date']

        nonce = web3.eth.get_transaction_count(acc1)
        balance = web3.eth.get_balance(acc1)

        # print(web3.from_wei(balance, 'ether'))
        # print("hetet")
    

        if balance < web3.to_wei(eth, 'ether'):
            return jsonify({'message': 'Insufficient balance for the transaction.'}), 400

        tx = {
            'nonce': nonce,
            'to': acc2,
            'value': web3.to_wei(eth, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        }

        signed_tx = web3.eth.account.sign_transaction(tx, p1)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        response = get_analysis(tx_name)

        transaction_hash = web3.to_hex(tx_hash)

        target.functions.addTransaction(web3.to_bytes(tx_hash), acc1, acc2, web3.to_wei(eth, 'ether'), tx_name, date).transact({'from': master_address})

        return jsonify({'transaction_hash': transaction_hash, "message" : "Transaction Succeessful", "analysis" : response}), 200
    except Exception as e:
        print("heerrreerer  ", e)
        return jsonify({'error': str(e)}), 500


@application.route('/make_account', methods=['POST'])
def make_account():
    try:
        p2 = request.form['pri_key']
        # print(p2)
        name = request.form['name']
        # print(name)
        date = request.form['date']

        image = request.form['image']
        print(image)

        acc2 = web3.eth.account.from_key(p2).address

        acc1 = "0xCFcdFD73e54790D49f41284D410fba42853D6543"
        p1 = "0x01bca0b57867634261a323ad85fc16d0ff2f7cae8b382bc8dc87f111b448a605"

        target.functions.setUserDetails(acc1, "GOD", 'https://unsplash.com/photos/a-cat-figurine-sitting-on-top-of-a-laptop-computer-q1avsArA3ro').transact({'from': acc1})
        

        nonce = web3.eth.get_transaction_count(acc1)
        
        balance = web3.eth.get_balance(acc1)

    

        if balance < web3.to_wei(100, 'ether'):
            return jsonify({'message': 'Insufficient balance for the transaction.'}), 400

        tx = {
            'nonce': nonce,
            'to': acc2,
            'value': web3.to_wei(100, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        }
        
        signed_tx = web3.eth.account.sign_transaction(tx, p1)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        target.functions.setUserDetails(acc2, name, image).transact({'from': acc1})

        target.functions.addTransaction(web3.to_bytes(tx_hash), acc1, acc2, web3.to_wei(100, "ether"), "Initialize", date).transact({'from': acc1})
 
        return jsonify({'transaction_hash': web3.to_hex(tx_hash), "address" : acc2, "private_key" : p2}), 200
    except Exception as e:
        print(e,"jjejejejjeejjjejejejejejejejejj")
        return jsonify({'error': str(e)}), 500
    

def get_balance_internal(address):
    try:

        return web3.from_wei( web3.eth.get_balance(address), "ether")
    except Exception as e:
        
        return e


def get_user_details_internal(address):
    try:
        name = target.functions.getUserDetails(address).call()
        # print(name)
        return name
    except Exception as e:
        print(e)

        return "error"

@application.route('/user_details', methods=['POST'])
def user_details():
    try:
        address = request.form['address']
        name = target.functions.getUserDetails(address).call()
        print(name)
        return jsonify({'username' : name[0],'image':name[1]}), 200
    except Exception as e:
        print(e)
        return "error"


@application.route('/get_all_transactions', methods=['POST'])
def get_all_transactions_for_account():
    try:
        account_address = request.form['address']
        transactions = []
        username = get_user_details_internal(account_address)[0]
        balance = str(get_balance_internal(account_address))

        # print(target.functions.getAllTransactionsForAccount(account_address).call())
        for tx_hash in target.functions.getAllTransactionsForAccount(account_address).call():
            
            sender_data = target.functions.getUserDetails(tx_hash[0]).call()
            sender = sender_data[0]
            sender_image = sender_data[1]

            receiver_data = target.functions.getUserDetails(tx_hash[1]).call()
            receiver = receiver_data[0]
            receiver_image = receiver_data[1]

            amount = web3.from_wei(tx_hash[2], "ether")
            name = tx_hash[3]
            date = tx_hash[4]

            myself = tx_hash[1] == account_address

            transactions.append({'from': sender, 'to': receiver, 'sender_image' : sender_image,'receiver_image' : receiver_image,'myself' : myself,'amt': str(amount), 'name': name, 'date' : date})
        
        # print(transactions)
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        return jsonify({'username' : username, "balance" : balance, 'transaction':transactions}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@application.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        address = request.form['address']
        
        
        balance = web3.from_wei( web3.eth.get_balance(address), "ether")

        return jsonify({"balance" : balance}), 200
    except Exception as e:
        
        return jsonify({'error': str(e)}), 500



def get_analysis(reason):
    try:
        
        GOOGLE_API_KEY= "AIzaSyAwrzXF46WDTtfxcRqv2HhiSv5i16ChAIY"
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(f"Please categorize the transaction from the user's reason given below, and I will provide you with categories. Return only the category.\n\nReason for Transaction: {reason}\nCategories: food expenses, bills, medical, finance, others")

        return response.text.lower()     
            
    except Exception as e:
        print(e)
        return "others"

@application.route('/buy_coin', methods=['POST'])
def buy_coin():
    try:
        acc1 = request.form['acc1']
        p1 = request.form['p1']
        price = request.form['price']
        tx_name = request.form['tx_name']
        date = request.form['date']

        eth = float(price) * 0.00030

        nonce = web3.eth.get_transaction_count(acc1)
        balance = web3.eth.get_balance(acc1)

        # print(web3.from_wei(balance, 'ether'))
        # print("hetet")
    

        if balance < web3.to_wei(eth, 'ether'):
            return jsonify({'message': 'Insufficient balance for the transaction.'}), 400

        tx = {
            'nonce': nonce,
            'to': master_address,
            'value': web3.to_wei(eth, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        }

        signed_tx = web3.eth.account.sign_transaction(tx, p1)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        response = get_analysis(tx_name)

        transaction_hash = web3.to_hex(tx_hash)
        target.functions.setUserDetails(master_address, "Crypto Buyer", 'https://unsplash.com/photos/a-cat-figurine-sitting-on-top-of-a-laptop-computer-q1avsArA3ro').transact({'from': master_address})

        target.functions.addTransaction(web3.to_bytes(tx_hash), acc1, master_address, web3.to_wei(eth, 'ether'), tx_name, date).transact({'from': master_address})

        return jsonify({'transaction_hash': transaction_hash, "message" : "Transaction Succeessful", "analysis" : response}), 200
    except Exception as e:
        print("heerrreerer  ", e)
        return jsonify({'error': str(e)}), 500

@application.route('/get_transactions', methods=['POST'])
def get_transactions():
    try:
        # account_address = request.form['address']
        transactions = []
       

        # print(target.functions.getAllTransactionsForAccount(account_address).call())
        for tx_hash in target.functions.getAllTransactions().call():
            
            sender_data = target.functions.getUserDetails(tx_hash[0]).call()
            sender = sender_data[0]
            sender_image = sender_data[1]

            receiver_data = target.functions.getUserDetails(tx_hash[1]).call()
            receiver = receiver_data[0]
            receiver_image = receiver_data[1]

            amount = web3.from_wei(tx_hash[2], "ether")
            name = tx_hash[3]
            date = tx_hash[4]

            # myself = tx_hash[1] == account_address

            transactions.append({'from': sender, 'to': receiver, 'sender_image' : sender_image,'receiver_image' : receiver_image,'amt': str(amount), 'name': name, 'date' : date})
        
        # print(transactions)
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        return jsonify({ 'transaction':transactions}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    application.run()

