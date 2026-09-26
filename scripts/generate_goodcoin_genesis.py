#!/usr/bin/env python3
"""
Goodcoin Genesis Block Generator - FAST VERSION FOR GOOGLE COLAB
Easy Difficulty - Generates in 1-2 Minutes
"""

import hashlib
import time
from datetime import datetime

def sha256(data):
    return hashlib.sha256(data).digest()

def double_sha256(data):
    return sha256(sha256(data))

def int_to_bytes(n, length):
    return n.to_bytes(length, "little")

def hex_to_bytes(s):
    return bytes.fromhex(s)

class GenesisGenerator:
    def __init__(self):
        self.version = 1
        self.prev_block = bytes(32)
        self.nTime = 1760000000
        self.nBits = 0x207fffff  # EASY DIFFICULTY - Fast mining
        self.nNonce = 0
        self.message = b"Goodcoin launched for fair and open digital money - 2026-09-26"
        self.reward = 250000000000000  # 2,500,000 GOOD in satoshis

    def create_coinbase_tx(self):
        tx = b""
        tx += int_to_bytes(1, 4)
        tx += b"\x01"
        tx += bytes(32)
        tx += int_to_bytes(0xffffffff, 4)

        script = bytes([0x04, 0xff, 0xff, 0x00, 0x1d, 0x04, 0x45])
        script += bytes([len(self.message)])
        script += self.message

        tx += int_to_bytes(len(script), 1)
        tx += script
        tx += int_to_bytes(0, 4)

        tx += b"\x01"
        tx += int_to_bytes(self.reward, 8)

        pubkey = hex_to_bytes("04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f")
        script_pubkey = bytes([len(pubkey)]) + pubkey + bytes([0xac])

        tx += int_to_bytes(len(script_pubkey), 1)
        tx += script_pubkey
        tx += int_to_bytes(0, 4)
        return tx

    def calculate_merkle_root(self, tx):
        return double_sha256(tx)

    def create_block_header(self, merkle_root, nonce):
        header = b""
        header += int_to_bytes(self.version, 4)
        header += self.prev_block
        header += merkle_root
        header += int_to_bytes(self.nTime, 4)
        header += int_to_bytes(self.nBits, 4)
        header += int_to_bytes(nonce, 4)
        return header

    def bits_to_target(self, nBits):
        """Convert nBits to target - Easy difficulty version"""
        nShift = (nBits >> 24) & 0xff
        coeff = nBits & 0x00ffffff
        if nShift <= 3:
            target = coeff >> (3 - nShift)
        else:
            target = coeff << (nShift - 3)
        return target

    def mine(self):
        coinbase_tx = self.create_coinbase_tx()
        merkle_root = self.calculate_merkle_root(coinbase_tx)

        print("=" * 70)
        print("🔗 GOODCOIN GENESIS BLOCK GENERATOR - FAST VERSION")
        print("=" * 70)
        print(f"\n📝 Message: {self.message.decode()}")
        print(f"💰 Reward: {self.reward / 100000000} GOOD")
        print(f"⏰ Time: {datetime.fromtimestamp(self.nTime)}")
        print(f"🎯 Difficulty Bits: 0x{self.nBits:08x} (EASY - Fast mining)")
        print("\n⛏️  Mining genesis block...")
        print("-" * 70)

        target = self.bits_to_target(self.nBits)
        print(f"Target: {hex(target)}\n")

        start = time.time()
        nonce = 0
        attempts = 0

        while True:
            header = self.create_block_header(merkle_root, nonce)
            h = double_sha256(header)

            attempts += 1

            # Check every 10000 attempts
            if attempts % 10000 == 0:
                elapsed = time.time() - start
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"⏳ Attempts: {attempts:,} | Rate: {rate:,.0f}/sec | Nonce: {nonce} | Time: {elapsed:.1f}s")

            # Convert hash to big-endian integer for comparison
            h_int = int.from_bytes(h, "big")

            if h_int <= target:
                elapsed = time.time() - start
                print("-" * 70)
                print(f"✅ FOUND! Time: {elapsed:.2f} seconds")
                print(f"✅ Total attempts: {attempts:,}")
                print("\n" + "=" * 70)
                print("🎉 GENESIS BLOCK PARAMETERS")
                print("=" * 70)
                print(f"\nNonce:        {nonce}")
                print(f"Block Hash:   {h.hex()}")
                print(f"Merkle Root:  {merkle_root.hex()}")
                print(f"Time:         {self.nTime}")
                print(f"Bits:         0x{self.nBits:08x}")
                print("\n" + "=" * 70)
                print("📋 COPY THESE VALUES TO src/kernel/chainparams.cpp:")
                print("=" * 70)
                print(f'\nconst char* goodcoin_genesis_msg = "Goodcoin launched for fair and open digital money - 2026-09-26";')
                print(f'genesis = CreateGenesisBlock(goodcoin_genesis_msg, goodcoin_genesis_script, {self.nTime}, {nonce}, 0x{self.nBits:08x}, 1, 2500000 * COIN);')
                print(f'consensus.hashGenesisBlock = uint256{{"' + h.hex() + '"}};')
                print(f'consensus.hashMerkleRoot = uint256{{"' + merkle_root.hex() + '"}};')
                print("\n" + "=" * 70)
                return {
                    'nonce': nonce,
                    'block_hash': h.hex(),
                    'merkle_root': merkle_root.hex(),
                    'time': self.nTime,
                    'bits': f'0x{self.nBits:08x}'
                }

            nonce += 1

def main():
    generator = GenesisGenerator()
    result = generator.mine()
    print("\n✅ Genesis block generated successfully!")
    print("✅ Ready to compile Goodcoin with these parameters!\n")

if __name__ == "__main__":
    main()
