
import hashlib
import json
import time
import uuid
import requests
from urllib.parse import urlparse

from flask import Flask,jsonify,request



class blockChain(object):	
	def __init__(self):
		self.chain=[]
		self.current_transactions=[]
		
		self.new_block(previous_hash=1, proof=100) #create创世区块
		
		self.nodes=set()
		
	def register_node(self,address):
		
		parsed_url=urlparse(address)
		self.nodes.add(parsed_url.netloc) #用set来避免重复node
	
	# valid the correct chain by proof and block_hash
	def valid_chain(self,chain):
		
		last_block=chain[0]
		current_index=1
		
		while current_index < len(chain):
			block=chain[current_index]
			print(str(last_block))
			print(str(block))
			print("\n-----------\n")
			#check hash is correct
			if block['previous_hash'] != self.hash(last_block):
				return False
			#check proof is correct	
			if not  self.valid_proof(last_block['proof'],block['proof']):
				return False
			
			last_block=block
			current_index += 1
				
		return True	
			
	def resolve_conflicts(self):
		
		neighbours_node=self.nodes
		new_chain=None
		
		max_length=len(self.chain)
		
		for node in neighbours_node:
			respone=requests.get('http://' + node + '/chain')
			if respone.status_code == 200:
				chain=respone.json()['chain']
				length=respone.json()['length']
				if length>max_length and self.valid_chain(chain):
					max_length=length
					new_chain=chain
		if new_chain:
			self.chain=new_chain
			return True
			
		return False
					
		
		
	def new_block(self,proof,previous_hash=None):
		"""
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
		
		block={
			'index':len(self.chain)+1,
			'timestamp':time.time(),
			'transactions':self.current_transactions,
			'proof':proof,
			'previous_hash':previous_hash or self.hash(self.chain[-1])
		
		}
		self.current_transactions=[]
		self.chain.append(block)
		return block
		
		
		
	def new_transaction(self,sender,recipient,amount):
		"""
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
		
		self.current_transactions.append({
			'sender':sender,
			'recipient':recipient,
			'amount':amount,
		})
		
		return self.last_block['index'] + 1 #待完善
		
	@staticmethod
	def hash(block):
		#hash a block
		"""
        生成块的 SHA-256 hash值
        :param block: <dict> Block
        :return: <str>
		"""
		
		block_string=json.dumps(block,sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()
		
		
	@property
	def last_block(self):
		return self.chain[-1]
		
		
		
	def proof_of_work(self,last_proof):
		"""
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """
		
		proof=0
		while self.valid_proof(last_proof,proof) is False:
			proof += 1
		return proof
		
		
	
	@staticmethod
	def valid_proof(last_proof,proof):
		"""
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
		string_rd=str(last_proof) + str(proof)
		#random_string=f'{last_proof}{proof}'.encode()
		random_string=string_rd.encode()
		rds_hash=hashlib.sha256(random_string).hexdigest()
		return rds_hash[:4] == '0000'
		
		
app=Flask(__name__)	
	
node_identifier=str(uuid.uuid4()).replace('-','')
	
blockchain=blockChain()
	
@app.route('/mine',methods=['GET'])
def mine():
	# We run the proof of work algorithm to get the next proof...
	last_block=blockchain.last_block
	last_proof=last_block['proof']
	proof=blockchain.proof_of_work(last_proof)
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1
	)
	
	block=blockchain.new_block(proof)
	respone={
		'message':"new block forged",
		'index':block['index'],
		'transactions':block['transactions'],
		'proof':block['proof'],
		'previous_hash':block['previous_hash'],
	}
	
	return jsonify(respone),200
	
@app.route('/transactions/new',methods=['POST'])
def new_transaction():
	values=request.get_json()
	required=['sender','recipient','amount']
	if not all(k in values for k in required):
		return 'missing values',400
	    #return "We'll add a new transaction"
	index=blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
	respone={'message': 'Transaction will be added to Block' + str(index) }
	return jsonify(respone),201

@app.route('/chain',methods=['GET'])	
def full_chain():
	respone={
		'chain':blockchain.chain,
		'length':len(blockchain.chain),
	}
	return jsonify(respone),200
	
@app.route('/node/register',methods=['POST'])
def register_nodes():
	nodes=request.get_json().get('nodes')
	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400
	
	for node in nodes:
		blockchain.register_node(node)
		
	respone={
		'message':'New nodes have been added',
		'totol_nodes':list(nodes)
	}

	return jsonify(respone),201

@app.route('/node/resolve',methods=['GET'])
def consensus():
	if blockchain.resolve_conflicts():
		response={'message':'Our chain was replaced',
				 'new_chain':blockchain.chain} 
	else:
		response={'message':'our chain is authorited',
				 'new_chain':blockchain.chain} 
	
	return jsonify(response), 200	
		
		
if __name__=='__main__':
	from argparse import ArgumentParser
	
	parser=ArgumentParser()
	parser.add_argument('-p','--port',default=5000,type=int,help='port to listen on')
	args=parser.parse_args()
	port=args.port
	
	app.run(host='127.0.0.1',port=port,debug=True)





	
		
		
		
		