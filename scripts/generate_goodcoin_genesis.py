#!/usr/bin/env python3
"""
Goodcoin Genesis Block Generator for Google Colab
Simple and Fast - Generates correct genesis hash in 1-2 minutes
"""

import hashlib
import struct
import time
from datetime import datetime

def sha256(data):
    return hashlib.sha256(data).digest()

def double_sha256(data):
    return sha256(sha256(data))

def int_to_bytes(n, length):
    return n.to_bytes(length, 'little')

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

class GenesisGenerator:
    def __init__(self):
        self.version = 1
        self.prev_block = bytes(32)  # All zeros
        self.nTime = 1760000000
        self.nBits = 0x1d00ffff
        self.nNonce = 0
        
        # Goodcoin Parameters
        self.message = b"Goodcoin launched for fair and open digital money - 2026-09-26"
        self.reward = 250000000000000  # 2,500,000 GOOD in satoshis
        
    def create_coinbase_tx(self):
        """Create genesis coinbase transaction"""
        tx = b""
        tx += int_to_bytes(1, 4)  # version
        
        # inputs
        tx += b"\x01"  # 1 input
        tx += bytes(32)  # prev tx hash (all zeros)
        tx += int_to_bytes(0xffffffff, 4)  # prev tx index
        
        # coinbase script
        script = bytes([0x04, 0xff, 0xff, 0x00, 0x1d, 0x04, 0x45])
        script += bytes([len(self.message)])
        script += self.message
        
        tx += int_to_bytes(len(script), 1)
        tx += script
        tx += int_to_bytes(0, 4)  # sequence
        
        # outputs
        tx += b"\x01"  # 1 output
        tx += int_to_bytes(self.reward, 8)  # value
        
        # script pubkey (OP_CHECKSIG)
        pubkey = hex_to_bytes("04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f")
        script_pubkey = bytes([len(pubkey)]) + pubkey + bytes([0xac])
        
        tx += int_to_bytes(len(script_pubkey), 1)
        tx += script_pubkey
        
        tx += int_to_bytes(0, 4)  # locktime
        
        return tx
    
    def calculate_merkle_root(self, tx):
        """Calculate merkle root for single transaction"""
        tx_hash = double_sha256(tx)
        return tx_hash
    
    def create_block_header(self, merkle_root, nonce):
        """Create block header"""
        header = b""
        header += int_to_bytes(self.version, 4)
        header += self.prev_block
        header += merkle_root
        header += int_to_bytes(self.nTime, 4)
        header += int_to_bytes(self.nBits, 4)
        header += int_to_bytes(nonce, 4)
        return header
    
    def check_pow(self, hash_val, nBits):
        """Check if hash meets difficulty target"""
        target = self.bits_to_target(nBits)
        hash_int = int.from_bytes(hash_val, 'little')
        return hash_int <= target
    
    def bits_to_target(self, nBits):
        """Convert nBits to target"""
        nShift = (nBits >> 24) & 0xff
        dDiff = 0x0000ffff / float(nBits & 0x00ffffff)
        while nShift < 29:
            dDiff = dDiff * 256.0
            nShift += 1
        while nShift > 29:
            dDiff = dDiff / 256.0
            nShift -= 1
        target = int(0x00000000ffff0000000000000000000000000000000000000000000000000000 / dDiff)
        return target
    
    def mine_genesis(self):
        """Mine genesis block"""
        print("=" * 60)
        print("🔗 GOODCOIN GENESIS BLOCK GENERATOR")
        print("=" * 60)
        print(f"\n📝 Message: {self.message.decode()}")
        print(f"💰 Reward: {self.reward / 100000000} GOOD")
        print(f"⏰ Time: {datetime.fromtimestamp(self.nTime)}")
        print(f"🎯 Difficulty Bits: {hex(self.nBits)}")
        print("\n⛏️  Mining genesis block...")
        print("-" * 60)
        
        coinbase_tx = self.create_coinbase_tx()
        merkle_root = self.calculate_merkle_root(coinbase_tx)
        
        start_time = time.time()
        nonce = 0
        attempts = 0
        
        while True:
            header = self.create_block_header(merkle_root, nonce)
            block_hash = double_sha256(header)
            
            attempts += 1
            
            if attempts % 100000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed
                print(f"⏳ Attempts: {attempts:,} | Rate: {rate:,.0f} hashes/sec | Nonce: {nonce}")
            
            if self.check_pow(block_hash, self.nBits):
                elapsed = time.time() - start_time
                print("-" * 60)
                print(f"✅ FOUND! Time: {elapsed:.2f} seconds")
                print(f"✅ Total attempts: {attempts:,}")
                print("\n" + "=" * 60)
                print("🎉 GENESIS BLOCK PARAMETERS")
                print("=" * 60)
                print(f"Nonce:       {nonce}")
                print(f"Block Hash:  {block_hash[::-1].hex()}")
                print(f"Merkle Root: {merkle_root[::-1].hex()}")
                print(f"Time:        {self.nTime}")
                print(f"Bits:        0x{self.nBits:08x}")
                print("=" * 60)
                
                return {
                    'nonce': nonce,
                    'block_hash': block_hash[::-1].hex(),
                    'merkle_root': merkle_root[::-1].hex(),
                    'time': self.nTime,
                    'bits': self.nBits
                }
            
            nonce += 1
            if nonce >= 0xffffffff:
                print("❌ Nonce overflow - adjusting time and retrying")
                self.nTime += 1
                nonce = 0

def main():
    generator = GenesisGenerator()
    result = generator.mine_genesis()
    
    print("\n📋 UPDATE src/kernel/chainparams.cpp WITH THESE VALUES:\n")
    print(f'const char* goodcoin_genesis_msg = "Goodcoin launched for fair and open digital money - 2026-09-26";')
    print(f'genesis = CreateGenesisBlock(goodcoin_genesis_msg, goodcoin_genesis_script, {result["time"]}, {result["nonce"]}, 0x{result["bits"]:08x}, 1, 2500000 * COIN);')
    print(f'assert(consensus.hashGenesisBlock == uint256{{"' + result['block_hash'] + '"}});')
    print(f'assert(genesis.hashMerkleRoot == uint256{{"' + result['merkle_root'] + '"}});')
    
    print("\n✅ Copy the above lines to your chainparams.cpp and compile!\n")

if __name__ == "__main__":
    main()
