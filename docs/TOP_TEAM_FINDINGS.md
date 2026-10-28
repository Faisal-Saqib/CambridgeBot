# Top-team gameplay findings and next experiments

> 2026-10-28 update: the census below was superseded by a full top-20 download —
> 1,040 ranked summaries across all 20 teams and 70 maps (1,869 team-games).
> Strategy prevalence ordered by usage: [TOP20_STRATEGY_CENSUS.md](TOP20_STRATEGY_CENSUS.md);
> per-map behaviour and 10 target points each: [TOP20_MAP_TARGETS.md](TOP20_MAP_TARGETS.md).
> Raw data, manifest and request logs: `matches/top20-scout/`.

Current instruction: every new unranked challenge must target a team currently ranked 1–20. This supersedes the earlier ±200-rating opponent rule. The previous peer campaign is closed to new requests, with 195 accepted results saved and 35 maps covered against all five peers. Its remaining 31 groups will not be submitted.

The new comparison uses v22 first, then a validated cohesion candidate against the same top-20 opponent submissions, maps, sides and seeds. Initial opponents were Intercontinental Fish (1), print dont int (4), hello (8), NEETCoders (12) and HBH (16). Rank is checked again immediately before each request; an opponent leaving the top 20 is not challenged.

## What the scouting sample contains

I captured the latest available finished ranked games for the then top three teams—Intercontinental Fish, Mite and Ad Astra—on The Line, Anvil, Stampede, Starfish, Expanse and Islands. This gives 18 team/map observations from 15 distinct games; some selected teams played each other. Selection did not depend on whether they won.

This is observational evidence, not a controlled comparison with our bot. Historical bot submission IDs are unavailable. Current ladder ranks identify the selected teams, not necessarily their rank at each game's start. The [observation table](TOP_TEAM_OBSERVATIONS.md) gives scores, deaths, upgrade spending, concentration of gold/damage and match IDs. The manifest, raw summaries, hashes and frozen analysis are under `matches/top-team-study-20261028/`.

Item spending is checked against `spentGold` using actual `buyItem` and `buyConsumable` events. Automatic emblem combinations are not counted as additional purchases. Kill participation joins the killer and unique credited assists from the same action and victim. Assists demonstrate involvement in a kill; they do not prove that a team maintained a particular spacing throughout a match.

## Concentrating upgrades is a credible candidate

Ad Astra's Vesper earned the largest share of team gold in all six sampled maps. In its five wins, that share was 64–74%.

| Ad Astra map | Vesper gold | Share of team gold | Other evidence |
| --- | ---: | ---: | --- |
| Anvil | 6,842 | 68.5% | 25 of 31 kills; 80.6% of team champion damage |
| Stampede | 8,179 | 67.2% | 12 of 13 kills; 73.6% of champion damage; 943 gems submitted |
| Starfish | 7,946 | 74.2% | 11 kills, no deaths; 658 gems submitted |
| Expanse | 5,532 | 64.6% | No champion kills; 32 of the team's 69 captures were Vesper alone |
| Islands | 5,140 | 64.3% | One kill; 31 of 62 captures were Vesper alone; 784 gems submitted |

Expanse shows that this concentration was not solely a reward for champion kills. Farming and item choices matter. These observations still do not establish intentional gold funneling: champion passives, routes, survival and item effects also affect income. Hunter and Collectors effects have not been verified, so their contribution is not assigned a guessed value.

The result is not universal. Intercontinental Fish's largest earner on The Line was Vendetta (55.5%), and Mite distributed that game's gold much more evenly (largest share 25.4%). Ad Astra's concentrated economy also lost The Line 0–1046 to Intercontinental Fish.

Candidate after cohesion is validated: let a chosen damage dealer collect selected gold-rich camps while healthy allies help clear and guard nearby. Rewards are shared among champions standing in the capture area when it finishes, so nearby support need not take an equal reward. Keep survival upgrades on the frontline, protect the collector's banking trip, and avoid turning a dangerous gem jackpot into one fragile carrier's entire bag. The SDK exposes purchases for the acting champion; there is no gold-transfer action in the inspected API.

## Focus is champion-dependent

Focus increases the effects specified by a champion's abilities. It does not automatically make attacks better against high-health targets. Strength scales basic attacks; health provides survival time. Choose investments from the kit and available attack opportunities.

- Vesper's kit has an attack reset and a movement dash, with no direct Focus-scaled damage spell. Strength is the natural damage investment for a Vesper carry.
- Cassi has a `2 × Focus` damage spell. Focus is relevant to her burst, with cooldown, casting restrictions and her linked death with Issac included in the risk.
- Marcella has both an attack reset and a `2 × Focus` spell. Strength versus Focus needs comparison; the successful Intercontinental Fish Anvil example had a largely Strength-based team build, with Marcella dealing 61% of team champion damage.
- Heart of Ruin gains a `1.5 × Focus` shield and a `1.5 × Focus` damaging/stunning dash, with a missing-health damage bonus. Focus can improve both protection and burst for that kit.

Our retained v22 already favors a shared combat target. Its target score uses enemy health relative to estimated damage, distance, gems and a large preference for the shared target. Coordinating attacks on a dangerous enemy is different from buying the Focus stat. High health alone is not a sufficient reason to choose a target; available damage, shields, reach, retaliation and support matter.

## Group combat matters, but capture does not require everyone

On The Line, Intercontinental Fish had four or five credited attackers in 17 of its 18 kills. Mite had at least four in 13 of 19 kills. Both drafted Vesper, Vendetta, Heart of Ruin and Cassi/Issac, giving five bodies from four picks.

They did not put everyone on every reward. Intercontinental Fish had a single recipient in 15 of 19 capture events; Mite had a single recipient in 26 of 27. Ad Astra's winning Anvil game had one recipient in 83 of 85 captures. A coordinated fighting group can let one member capture while others protect it or do nearby useful work.

This supports testing shared routes and nearby support. It does not support indefinite waiting or forcing every champion onto the same tile. Our archived v23 formed separate subgroups and exempted carriers from regrouping; the new local candidate addresses those gaps with shared rally information and coordinated objectives.

## Implementation and evidence status

`bots/cohesion` is an isolated experiment based on v22. Its first revision compiled but lost all 12 focused local games, with 464 total gems submitted and no engine-reported bot faults. It is not suitable for promotion. The failed records are preserved under `matches/panel-cohesion-20261028-151640/`; movement and mode transitions need diagnosis before another comparison.

Live v22 remains the baseline while the top-20 panel is collected. The current candidate is described separately in [cohesion-local](strategies/cohesion-local.md). Concentrated upgrades, alternate drafts and item changes remain separate experiments, so their effects are not confused with formation changes.
