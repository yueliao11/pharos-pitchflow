const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentVideoRegistry", function () {
  async function deployFixture() {
    const [agent, creator] = await ethers.getSigners();
    const Registry = await ethers.getContractFactory("AgentVideoRegistry");
    const registry = await Registry.deploy();
    return { registry, agent, creator };
  }

  it("Should register a video and emit VideoRegistered", async function () {
    const { registry, agent, creator } = await deployFixture();

    const contentHash = ethers.encodeBytes32String("demo-hash");
    await expect(
      registry
        .connect(creator)
        .registerVideo(
          agent.address,
          "Demo Video",
          "https://example.com/video.mp4",
          "https://example.com/metadata.json",
          contentHash
        )
    )
      .to.emit(registry, "VideoRegistered")
      .withArgs(0, agent.address, creator.address, contentHash, "https://example.com/video.mp4", "https://example.com/metadata.json");

    const video = await registry.getVideo(0);
    expect(video.title).to.equal("Demo Video");
    expect(video.agent).to.equal(agent.address);
    expect(video.creator).to.equal(creator.address);
    expect(video.contentHash).to.equal(contentHash);
  });

  it("Should reject duplicate content hashes", async function () {
    const { registry, agent, creator } = await deployFixture();
    const contentHash = ethers.encodeBytes32String("dup-hash");

    await registry
      .connect(creator)
      .registerVideo(agent.address, "First", "uri", "meta", contentHash);

    await expect(
      registry
        .connect(creator)
        .registerVideo(agent.address, "Second", "uri2", "meta2", contentHash)
    ).to.be.revertedWith("Content already registered");
  });
});
