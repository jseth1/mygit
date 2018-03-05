import hashlib
import time

max_nonce=2 ** 32 

def proof_of_work(header,difficulty_bits):
	target=2 ** (256-difficulty_bits)
	
	for nonce in range(max_nonce):
		hash_result=hashlib.sha256((str(header)+str(nonce)).encode("utf-8")).hexdigest()
		
		if  int(hash_result,16)<target:
			print("success with nonce %d" % nonce)
			print("hash is %s" % hash_result)
			return(hash_result,nonce)
			
	print ("failed after %d (max_nonce) tries" % nonce)
	return nonce
	
if __name__=='__main__':
		nonce=0;
		hash_result=''
		
		for difficulty_bits in range(32):
			difficulty=2 ** difficulty_bits
			print ("difficulty: %1d(%d bits)" %(difficulty,difficulty_bits) )
			print("start search...")
			
			start_time=time.time()
			new_block='test block with transactions' + hash_result
			(hash_result,nonce)=proof_of_work(new_block,difficulty_bits)
			end_time=time.time()
			elapsed_time=end_time-start_time
			print("elapsed time: %.4f seconds" % elapsed_time)
			
			if elapsed_time>0:
				hash_power=float(nonce/elapsed_time)
				print ("Hashing Power: %ld hashes per second" % hash_power) 
			
			
			
			
			
			
			
			
			
			
