require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000";
const PHAROS_RPC = process.env.PHAROS_RPC || "https://testnet.pharosnetwork.xyz";
const PHAROS_CHAIN_ID = parseInt(process.env.PHAROS_CHAIN_ID || "500", 10);

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      chainId: 1337,
    },
    pharos_testnet: {
      url: PHAROS_RPC,
      chainId: PHAROS_CHAIN_ID,
      accounts: [PRIVATE_KEY],
    },
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};
