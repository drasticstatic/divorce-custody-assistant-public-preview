## The journey behind this record (brief, pre-2026)

This compliance log opens on January 2026, but the labor it documents did not
begin then. The dated weekly entries below are the later chapter of an arc that
was already underway. This brief summary frames what came before, grounded in
the public repository record, so the dated log is read in its proper context.

**1. Classroom — the DappUniversity blockchain bootcamp (May – Sep 2025).**
The craft underlying this practice was built in an immersive
blockchain-developer bootcamp: smart-contract fundamentals, Hardhat workflows,
and the canonical capstones built in sequence:

| Created | Repository | Capstone |
|---|---|---|
| 2025-05-01 | `blockchain-developer-bootcamp`, `hardhat_example` | Course foundations, Hardhat tooling |
| 2025-05-17 | `crowdsale` | Token crowdsale contract |
| 2025-06-21 | `dao` | Decentralized autonomous organization |
| 2025-07-16 | `nft_dappu-punks` | NFT dapp |
| 2025-07-27 | `solidity_intensive` | Solidity intensive |
| 2025-09-21 | `amm` | Automated market-maker |

These repos remain public on the maintainer's GitHub as the verifiable record
of the schooling. The `code-forked/` local working directory holds curated
working copies of upstream open-source projects studied and integrated into
the trading system (attribution below).

**2. First product + portfolio (May – Dec 2025).** The classroom met practice
early: the first product — a gratitude-token project (created 2025-05-25) — and
the first trading bot, an arbitrage dapp over the DappUniversity v3 curriculum
(`trading-bot_arbitrage_DAPPUv3_hardhat_UNI-CAKE`, created 2025-07-18). During
this phase the work was migrated off the local machine and onto GitHub Pages:
early publish experiments (the `gratitude-token-project_testPublish_*`
repositories of Oct 2025 and Jan 2026), a public docs surface
(`gratitude-token-project_docs`, 2025-10-09), local directory
reorganization, older work forked-and-curated, and a `resume` repository
(2025-12-12) anchoring the portfolio. The purpose of this phase was to make the
learning visible and attributable — the same honesty contract this compliance
record runs on.

**3. Practice — the startup pivot (Feb 2026 → present).** Classroom-to-product
at scale: the `trading-assistant` quantitative-trading platform (private
2026-02-21 → public-preview 2026-02-22), a personal developer portal
(`drasticstatic.github.io`, 2026-03-11), the multi-repo dev ecosystem, and a
cluster of market-data and automation MCP integrations stood up together at the
end of April 2026 (`tradingview-mcp-jackson`, `robinhood-mcp`, `hummingbot-mcp`,
`hummingbot-api`). This is the phase the weekly log below documents in
attributable, dated detail from January 2026 forward.

### Attribution — the `code-forked/` working set (curated upstream copies)

Not every repo in the record is authored from scratch. The `code-forked/`
directory holds curated working copies of upstream open-source projects that
were studied, integrated, and in some cases extended for the trading system.
Public attribution of those upstreams:

| Working copy (`drasticstatic/`) | Upstream | Purpose |
|---|---|---|
| `free-claude-code` | [`Alishahryar1/free-claude-code`](https://github.com/Alishahryar1/free-claude-code) | Anthropic-compatible proxy for NVIDIA NIM / DeepSeek / OpenRouter / Ollama (powers the multi-agent dev system) |
| `hummingbot` | [`hummingbot/hummingbot`](https://github.com/hummingbot/hummingbot) | Open-source crypto market-making / arbitrage bot engine |
| `hummingbot-mcp` | [`hummingbot/mcp`](https://github.com/hummingbot/mcp) | Model Context Protocol layer for the bot |
| `hummingbot-api` | [`hummingbot/hummingbot-api`](https://github.com/hummingbot/hummingbot-api) | Python REST/WebSocket client for the Hummingbot API server |
| `robinhood-mcp` | [`verygoodplugins/robinhood-mcp`](https://github.com/verygoodplugins/robinhood-mcp) | MCP layer for the Robinhood brokerage (equities/options market data) |
| `tradingview-mcp-jackson` | [`LewisWJackson/tradingview-mcp-jackson`](https://github.com/LewisWJackson/tradingview-mcp-jackson) | MCP layer for the TradingView desktop client (charting / signal flow) |

The maintainer's value-add is the integration, configuration, trading-strategy
work, and the higher-order multi-agent system these plugs into — not the claim
of authoring the upstream libraries themselves. The upstream repos are linked
above so attribution is explicit and verifiable.

> **On dating.** The classroom capstones were migrated to GitHub after the
> instruction; their repository *creation* dates above post-date the actual
> coursework. What is certain and verifiable: the practice this compliance
> record evidences did not begin on January 1, 2026 — it is the harvest of an
> intensive classroom → product → portfolio arc that was in motion through all
> of 2025.

The repos named above are independently verifiable on the maintainer's public
GitHub profile at `https://github.com/drasticstatic` (the private product repos
each have a public `-public-preview` or `-public` mirror, which is the lane the
dated log below counts).
