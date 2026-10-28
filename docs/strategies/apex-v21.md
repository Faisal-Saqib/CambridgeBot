# apex v21 - smaller tribute hauls and wards (online trial rejected)

Frozen source: bots/apex21. Submitted as 09e1c9c5-23a3-43a4-92c0-d48859558a9e. Working bots/apex was ultimately restored to the retained v22 implementation.

## Changes from v20

1. **Lower tribute limits** (`bank.rs`, constants at the top).

   | Situation | Anywhere | Altar within 15 tiles | Altar within 4 tiles |
   | --- | --- | --- | --- |
   | Normal | 30 gems | 15 gems | 5 gems |
   | Threatened, or Marcella | 15 gems | 8 gems | 5 gems |

   v20 waited for 40–60 gems (Marcella/careful: 20). "Threatened" (`Bot::threatened`) means any of:
   - an enemy champion seen within 14 tiles in the last 40 rounds;
   - a teammate died in the last 100 rounds;
   - below 60% HP.

   Endgame rule kept: tribute whenever banked + carried ≥ 1000.
2. **Wards** (`Bot::place_ward`, called every turn). When the free ward is ready:
   - next to an altar we are standing by (watch for altar ambushes);
   - otherwise, if our current ward is more than 8 tiles away, on the reachable tile within 2 tiles closest to the enemy spawn.

## Expected strong points
- Far fewer carried gems lost on death, and kills on us score less for the enemy.
- Earlier sight of enemies around our farming area and our altars.

## Expected weak points / risks
- More walking to altars (more, shorter trips); could slow farming on big maps.
- Ward placement is simple; vision only helps its owner.

## Verification and decision

The CLI resumed. v21 compiled and completed a local release panel: 8/10 against apex20 on five maps, both sides, with zero bot faults. Ten online games then reused the baseline maps/sides and saved opponent submissions: 0-5 against Ascendance and 2-3 against QS2 (2/10 total), compared with baseline 4/10. All ten map hashes, seeds and engine builds match the baseline.

Our average tribute was 22.44 gems versus 31.62, but deaths rose 174 versus 134 and fuel exhaustions 890 versus 284. No bot faults. The combined change was rejected on this evidence. Ward placement is not proven to be the sole cause. v22 isolates smaller banking limits without wards. [Full results and provenance](../online-cycle-20261027.md).
