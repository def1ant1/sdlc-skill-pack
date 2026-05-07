# Channel Routing Rules

Used by `core/gtm-orchestration/SKILL.md` to recommend channel mix, priority order, and
budget allocation based on product type, audience, and primary GTM goal.

---

## Channel Mix by Product and Audience

| Product Type | Audience | Primary Goal | Recommended Channels | Priority Order |
|---|---|---|---|---|
| B2B SaaS | SMB decision-makers | Pipeline / demos | SEO, LinkedIn Ads, cold email, G2/Capterra | SEO → LinkedIn → Email → Review sites |
| B2B SaaS | Enterprise buyers | Brand + pipeline | Thought leadership, events, ABM, PR | Events → PR → ABM → Content |
| B2C Consumer App | Mass market | Downloads / signups | Meta Ads, TikTok, influencer, SEO, ASO | Paid social → Influencer → SEO |
| Developer Tool | Engineers / OSS | Adoption / stars | HN, Reddit, Dev.to, GitHub, OSS communities | Community → Content → OSS → Paid |
| AI Product | Technical + non-technical | Awareness + trial | AI directories, Product Hunt, LinkedIn, SEO, AI newsletters | AI dirs → PH → LinkedIn → Newsletter |
| API / Infrastructure | Developers / CTOs | Integration / usage | Developer docs, GitHub, API marketplaces, DevRel | Docs → GitHub → DevRel → Community |
| Enterprise Platform | C-suite / VP | RFP / procurement | Analyst relations, events, direct sales, PR | Analyst → Events → PR → Direct |
| Marketplace / Platform | Two-sided market | Supply + demand | SEO, paid, partnerships, virality | SEO → Partnerships → Paid → Viral |

---

## Budget Allocation Guidance

| Channel | Stage | Budget % Guidance | Timeline to Results |
|---|---|---|---|
| SEO / Content | Awareness | 15–25% | 3–6 months |
| AI Search Optimization | Awareness | 5–10% | 1–3 months |
| Paid Search (Google) | Demand capture | 15–25% | 2–4 weeks |
| Paid Social (Meta/LinkedIn) | Awareness + demand gen | 15–30% | 2–6 weeks |
| Developer Relations | Adoption | 10–20% | 3–9 months |
| Product Hunt / Directories | Launch spike | 5–10% | Launch week |
| Influencer / Partnership | Trust + reach | 10–20% | 4–8 weeks |
| Email / CRM | Retention + expansion | 5–10% | 2–4 weeks |
| Events / Conferences | Enterprise pipeline | 10–20% | 3–6 months |
| PR / Analyst Relations | Brand credibility | 5–15% | 1–3 months |

*Allocations are guidelines; adjust based on product-market fit signals and CAC data.*

---

## Channel Selection Rules

1. **Stage-first**: Match channels to funnel stage (awareness → consideration → conversion → retention).
2. **Audience-native**: Go where the audience already is — don't force B2B buyers into TikTok.
3. **CAC discipline**: Set a maximum acceptable CAC per channel before launch; kill channels that exceed it by 2× after 60 days.
4. **Sequencing**: Organic and community channels before paid — validate messaging on low-cost channels first.
5. **AI visibility**: Every product launch must include AI search optimization (llms.txt, capability manifest) regardless of product type. AI-driven discovery is now a baseline channel.

---

## Disqualifying Signals

| Signal | Channel to Deprioritize | Reason |
|---|---|---|
| No brand search volume | Paid search (brand) | No demand to capture yet |
| < 50 DA on domain | Direct SEO push | Insufficient authority; build links first |
| Developer-only audience | Meta Ads, TikTok | Wrong platform; use GitHub/HN/Dev.to |
| < $5K/month budget | Events, analyst relations | Minimum threshold not met |
| No landing page live | Any paid channel | Wasted spend without conversion path |