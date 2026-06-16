const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  const Registry = await ethers.getContractFactory("AgentVideoRegistry");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  const registryAddress = await registry.getAddress();
  console.log("AgentVideoRegistry deployed to:", registryAddress);

  const PaymentGate = await ethers.getContractFactory("PaymentGate");
  const paymentGate = await PaymentGate.deploy();
  await paymentGate.waitForDeployment();
  const paymentAddress = await paymentGate.getAddress();
  console.log("PaymentGate deployed to:", paymentAddress);

  console.log("\nAdd these to your backend .env:");
  console.log(`PHAROS_REGISTRY_ADDRESS=${registryAddress}`);
  console.log(`PHAROS_PAYMENT_ADDRESS=${paymentAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
