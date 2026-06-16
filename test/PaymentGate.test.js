const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PaymentGate", function () {
  async function deployFixture() {
    const [payer, agent] = await ethers.getSigners();
    const PaymentGate = await ethers.getContractFactory("PaymentGate");
    const paymentGate = await PaymentGate.deploy();
    return { paymentGate, payer, agent };
  }

  it("Should accept payment and update balance", async function () {
    const { paymentGate, payer, agent } = await deployFixture();
    const contentHash = ethers.encodeBytes32String("pay-hash");

    await expect(
      paymentGate
        .connect(payer)
        .payForContent(agent.address, contentHash, "purchase", { value: ethers.parseEther("0.1") })
    )
      .to.emit(paymentGate, "PaymentReceived")
      .withArgs(payer.address, agent.address, contentHash, ethers.parseEther("0.1"), "purchase");

    expect(await paymentGate.balances(agent.address)).to.equal(ethers.parseEther("0.1"));
  });

  it("Should allow agent to withdraw", async function () {
    const { paymentGate, payer, agent } = await deployFixture();
    const contentHash = ethers.encodeBytes32String("tip-hash");

    await paymentGate
      .connect(payer)
      .tipAgent(agent.address, contentHash, { value: ethers.parseEther("0.05") });

    const before = await ethers.provider.getBalance(agent.address);
    await paymentGate.connect(agent).withdraw();
    const after = await ethers.provider.getBalance(agent.address);

    expect(after).to.be.gt(before);
    expect(await paymentGate.balances(agent.address)).to.equal(0);
  });
});
