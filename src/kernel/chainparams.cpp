// Copyright (c) 2010 Satoshi Nakamoto
// Copyright (c) 2009-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <kernel/chainparams.h>

#include <chainparamsseeds.h>
#include <consensus/amount.h>
#include <consensus/merkle.h>
#include <consensus/params.h>
#include <crypto/hex_base.h>
#include <kernel/messagestartchars.h>
#include <kernel/signet.h>
#include <primitives/block.h>
#include <primitives/transaction.h>
#include <script/interpreter.h>
#include <script/script.h>
#include <script/verify_flags.h>
#include <uint256.h>
#include <util/chaintype.h>
#include <util/log.h>
#include <util/strencodings.h>

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iterator>
#include <map>
#include <span>
#include <utility>

using namespace util::hex_literals;

static CBlock CreateGenesisBlock(const char* pszTimestamp, const CScript& genesisOutputScript, uint32_t nTime, uint32_t nNonce, uint32_t nBits, int32_t nVersion, const CAmount& genesisReward)
{
    CMutableTransaction txNew;
    txNew.version = 1;
    txNew.vin.resize(1);
    txNew.vout.resize(1);
    txNew.vin[0].scriptSig = CScript() << 486604799 << CScriptNum(4) << std::vector<unsigned char>((const unsigned char*)pszTimestamp, (const unsigned char*)pszTimestamp + strlen(pszTimestamp));
    txNew.vout[0].nValue = genesisReward;
    txNew.vout[0].scriptPubKey = genesisOutputScript;

    CBlock genesis;
    genesis.nTime    = nTime;
    genesis.nBits    = nBits;
    genesis.nNonce   = nNonce;
    genesis.nVersion = nVersion;
    genesis.vtx.push_back(MakeTransactionRef(std::move(txNew)));
    genesis.hashPrevBlock.SetNull();
    genesis.hashMerkleRoot = BlockMerkleRoot(genesis);
    return genesis;
}

/**
 * Build the genesis block. Note that the output of its generation
 * transaction cannot be spent since it did not originally exist in the
 * database.
 *
 * CBlock(hash=2d1151ce, ver=1, hashPrevBlock=00000000000000, hashMerkleRoot=65711d08, nTime=1760000000, nBits=207fffff, nNonce=5000001, vtx=1)
 *   CTransaction(hash=65711d08, ver=1, vin.size=1, vout.size=1, nLockTime=0)
 *     CTxIn(COutPoint(000000, -1), coinbase "Goodcoin launched for fair and open digital money - 2026-09-26")
 *     CTxOut(nValue=2500000.00000000, scriptPubKey=OP_CHECKSIG)
 */
static CBlock CreateGenesisBlock(uint32_t nTime, uint32_t nNonce, uint32_t nBits, int32_t nVersion, const CAmount& genesisReward)
{
    const char* pszTimestamp = "Goodcoin launched for fair and open digital money - 2026-09-26";
    const CScript genesisOutputScript = CScript() << "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"_hex << OP_CHECKSIG;
    return CreateGenesisBlock(pszTimestamp, genesisOutputScript, nTime, nNonce, nBits, nVersion, genesisReward);
}

void CChainParams::ApplyDeploymentOptions(const DeploymentOptions& opts)
{
    for (const auto& [dep, height] : opts.activation_heights) {
        switch (dep) {
        case Consensus::BuriedDeployment::DEPLOYMENT_SEGWIT:
            consensus.SegwitHeight = int{height};
            break;
        case Consensus::BuriedDeployment::DEPLOYMENT_HEIGHTINCB:
            consensus.BIP34Height = int{height};
            break;
        case Consensus::BuriedDeployment::DEPLOYMENT_DERSIG:
            consensus.BIP66Height = int{height};
            break;
        case Consensus::BuriedDeployment::DEPLOYMENT_CLTV:
            consensus.BIP65Height = int{height};
            break;
        case Consensus::BuriedDeployment::DEPLOYMENT_CSV:
            consensus.CSVHeight = int{height};
            break;
        }
    }

    for (const auto& [deployment_pos, version_bits_params] : opts.version_bits_parameters) {
        consensus.vDeployments[deployment_pos].nStartTime = version_bits_params.start_time;
        consensus.vDeployments[deployment_pos].nTimeout = version_bits_params.timeout;
        consensus.vDeployments[deployment_pos].min_activation_height = version_bits_params.min_activation_height;
    }
}

/**
 * Main network on which people trade goods and services.
 */
class CMainParams : public CChainParams {
public:
    CMainParams(const MainNetOptions& opts) {
        m_chain_type = ChainType::MAIN;
        consensus.signet_blocks = false;
        consensus.signet_challenge.clear();
        consensus.nSubsidyHalvingInterval = 210000;
        consensus.script_flag_exceptions.emplace( // BIP16 exception
            uint256{"00000000000002dc756eebf4f49723ed8d30cc28a5f108eb94b1ba88ac4f9c22"}, SCRIPT_VERIFY_NONE);
        consensus.script_flag_exceptions.emplace( // Taproot exception
            uint256{"0000000000000000000f14c35b2d841e986ab5441de8c585d5ffe55ea1e395ad"}, SCRIPT_VERIFY_P2SH | SCRIPT_VERIFY_WITNESS);
        consensus.BIP34Height = 227931;
        consensus.BIP34Hash = uint256{"000000000000024b89b42a942fe0d9fea3bb44ab7bd1b19115dd6a759c0808b8"};
        consensus.BIP65Height = 388381;
        consensus.BIP66Height = 363725;
        consensus.CSVHeight = 419328;
        consensus.SegwitHeight = 481824;
        consensus.MinBIP9WarningHeight = 711648;
        consensus.powLimit = uint256{"00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"};
        consensus.nPowTargetTimespan = 14 * 24 * 60 * 60; // two weeks
        consensus.nPowTargetSpacing = 10 * 60;
        consensus.fPowAllowMinDifficultyBlocks = false;
        consensus.enforce_BIP94 = false;
        consensus.fPowNoRetargeting = false;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].bit = 28;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].nStartTime = Consensus::BIP9Deployment::NEVER_ACTIVE;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].nTimeout = Consensus::BIP9Deployment::NO_TIMEOUT;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].min_activation_height = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].threshold = 1815; // 90%
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].period = 2016;

        ApplyDeploymentOptions(opts.dep_opts);

        consensus.nMinimumChainWork = uint256{"000000000000000000000000000000000000000145ec036acc5ba740052af1a0"};
        consensus.defaultAssumeValid = uint256{"00000000000000000000748969ec33043c0e52a763c6dd5193861f559f2c72e3"};

        /**
         * The message start string is designed to be unlikely to occur in normal data.
         * The characters are rarely used upper ASCII, not valid as UTF-8, and produce
         * a large 32-bit integer with any alignment.
         */
        pchMessageStart[0] = 0x47;
        pchMessageStart[1] = 0x4f;
        pchMessageStart[2] = 0x4f;
        pchMessageStart[3] = 0x44;
        nDefaultPort = 9333;
        nPruneAfterHeight = 100000;
        m_assumed_blockchain_size = 897;
        m_assumed_chain_state_size = 14;

        const char* goodcoin_genesis_msg = "Goodcoin launched for fair and open digital money - 2026-09-26";
        const CScript goodcoin_genesis_script = CScript() << "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"_hex << OP_CHECKSIG;
        genesis = CreateGenesisBlock(goodcoin_genesis_msg, goodcoin_genesis_script, 1760000000, 5000001, 0x207fffff, 1, 2500000 * COIN);
        consensus.hashGenesisBlock = genesis.GetHash();
        assert(consensus.hashGenesisBlock == uint256{"2d1151ce687c9e16cf8c10d20fc0ff6792be13866e39211119a1007afc0c091e"});
        assert(genesis.hashMerkleRoot == uint256{"65711d08a717add7f52d1ff5086a02f95d0f445c7a85737ed6752379a7787f92"});

        // Goodcoin seed nodes - will be populated later
        vSeeds.clear();
        
        base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1, 0x26);
        base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1, 0x1c);
        base58Prefixes[SECRET_KEY] =     std::vector<unsigned char>(1, 0x80);
        base58Prefixes[EXT_PUBLIC_KEY] = {0x04, 0x88, 0xB2, 0x1E};
        base58Prefixes[EXT_SECRET_KEY] = {0x04, 0x88, 0xAD, 0xE4};

        bech32_hrp = "good";
        silent_payments_hrp = "gsp";

        vFixedSeeds = std::vector<uint8_t>(std::begin(chainparams_seed_main), std::end(chainparams_seed_main));

        fDefaultConsistencyChecks = false;
        m_is_mockable_chain = false;

        m_assumeutxo_data = {};

        chainTxData = ChainTxData{
            .nTime    = 1760000000,
            .tx_count = 1,
            .dTxRate  = 0.0,
        };

        m_headers_sync_params = HeadersSyncParams{
            .commitment_period = 649,
            .redownload_buffer_size = 15400,
        };
    }
};
