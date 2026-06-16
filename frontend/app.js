const API_BASE = window.location.hostname === "localhost"
  ? "http://localhost:8000"
  : "";

const PAYMENT_ABI = [
  "function payForContent(address agent, bytes32 contentHash, string reason) payable",
  "function tipAgent(address agent, bytes32 contentHash) payable",
  "function balances(address) view returns (uint256)",
  "event PaymentReceived(address indexed payer, address indexed beneficiary, bytes32 indexed contentHash, uint256 amount, string reason)"
];

let signer = null;
let provider = null;

// ---------- Video generation ----------
document.getElementById("generateForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = document.getElementById("pptxFile").files[0];
  if (!file) return alert("Please select a PPTX file.");

  const formData = new FormData();
  formData.append("pptx_file", file);
  formData.append("script_mode", document.getElementById("scriptMode").value);
  formData.append("voice", document.getElementById("voice").value);
  formData.append("language", document.getElementById("language").value);
  formData.append("video_style", document.getElementById("videoStyle").value);
  formData.append("output_format", "mp4");
  formData.append("include_subtitles", document.getElementById("includeSubtitles").checked);
  formData.append("watermark", "false");
  formData.append("register_onchain", document.getElementById("registerOnchain").checked);

  const progress = document.getElementById("progress");
  const btn = document.getElementById("generateBtn");
  progress.classList.remove("hidden");
  btn.disabled = true;

  try {
    const resp = await fetch(`${API_BASE}/skill/generate`, {
      method: "POST",
      body: formData,
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "Generation failed");

    renderResult(data);
  } catch (err) {
    alert(err.message);
  } finally {
    progress.classList.add("hidden");
    btn.disabled = false;
  }
});

function renderResult(data) {
  const card = document.getElementById("resultCard");
  card.style.display = "block";

  const video = document.getElementById("previewVideo");
  video.src = data.video_url;
  video.poster = data.cover_image_url;

  document.getElementById("videoLink").href = data.video_url;
  document.getElementById("subtitleLink").href = data.subtitle_url;
  document.getElementById("coverLink").href = data.cover_image_url;
  document.getElementById("metadataLink").href = data.metadata_url;
  document.getElementById("resultJson").textContent = JSON.stringify(data, null, 2);

  // Pre-fill payment fields for convenience.
  if (data.pharos_tx_hash) {
    document.getElementById("txInfo").textContent = `Registered on Pharos: ${data.pharos_tx_hash}`;
  }
}

// ---------- Wallet & tipping ----------
document.getElementById("connectWallet").addEventListener("click", async () => {
  if (!window.ethereum) return alert("MetaMask not found.");
  provider = new ethers.BrowserProvider(window.ethereum);
  await provider.send("eth_requestAccounts", []);
  signer = await provider.getSigner();
  const address = await signer.getAddress();
  document.getElementById("walletInfo").textContent = `Connected: ${address}`;
  document.getElementById("tipBtn").disabled = false;
});

document.getElementById("tipBtn").addEventListener("click", async () => {
  if (!signer) return alert("Connect wallet first.");
  const paymentAddress = document.getElementById("paymentAddress").value.trim();
  const agentAddress = document.getElementById("agentAddress").value.trim();
  const amount = document.getElementById("tipAmount").value;

  if (!paymentAddress || !agentAddress) {
    return alert("Please enter PaymentGate and Agent addresses.");
  }

  const contract = new ethers.Contract(paymentAddress, PAYMENT_ABI, signer);
  const contentHash = document.getElementById("resultJson")
    ? JSON.parse(document.getElementById("resultJson").textContent).content_hash
    : ethers.ZeroHash;

  try {
    const tx = await contract.payForContent(
      agentAddress,
      "0x" + contentHash,
      "tip",
      { value: ethers.parseEther(amount.toString()) }
    );
    document.getElementById("txInfo").textContent = `Transaction sent: ${tx.hash}`;
    await tx.wait();
    document.getElementById("txInfo").textContent = `Confirmed: ${tx.hash}`;
  } catch (err) {
    alert(err.message);
  }
});
