pub const SLOTS: usize = 6;
pub const TRAVEL: u8 = 0;
pub const BANK: u8 = 1;
pub const HOME: u8 = 2;

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Packet {
    pub leader: Option<usize>,
    pub pos: (i32, i32),
    pub round: u16,
    pub mode: u8,
    pub goal: Option<usize>,
    pub claims: u8,
    pub focus: Option<usize>,
    pub gates: u8,
}
fn enc(value: Option<usize>, limit: usize) -> u8 {
    value.filter(|v| *v < limit).map_or(0, |v| (v + 1) as u8)
}
fn dec(value: u8) -> Option<usize> {
    (value != 0).then(|| value as usize - 1)
}
impl Packet {
    pub fn decode(b: [u8; 8]) -> Self {
        Self {
            leader: dec(b[0]).filter(|v| *v < SLOTS),
            pos: (b[1] as i32, b[2] as i32),
            round: u16::from_le_bytes([b[6], b[7]]),
            mode: (b[5] >> 5) & 3,
            goal: dec(b[3]), claims: b[4] & 63,
            focus: dec(b[5] & 7).filter(|v| *v < SLOTS),
            gates: (b[5] >> 3) & 3,
        }
    }
    pub fn encode(self) -> [u8; 8] {
        assert!((0..=255).contains(&self.pos.0) && (0..=255).contains(&self.pos.1));
        let r = self.round.to_le_bytes();
        [enc(self.leader, SLOTS), self.pos.0 as u8, self.pos.1 as u8,
         enc(self.goal, 255), self.claims & 63,
         enc(self.focus, SLOTS) | ((self.gates & 3) << 3) | ((self.mode & 3) << 5), r[0], r[1]]
    }
    pub fn publish(&mut self, slot: usize, pos: (i32, i32), round: u32, mode: u8) {
        if self.leader != Some(slot) || self.mode != mode {
            self.goal = None;
            self.claims = 0;
        }
        self.leader = Some(slot);
        self.pos = pos;
        self.round = round.min(u16::MAX as u32) as u16;
        self.mode = mode;
    }
    pub fn claim_of(self, slot: usize) -> Option<usize> {
        if slot < SLOTS && self.mode == TRAVEL && self.claims & (1 << slot) != 0 { self.goal } else { None }
    }
    pub fn set_claim(&mut self, slot: usize, job: Option<usize>) {
        if slot >= SLOTS { return; }
        let job = job.filter(|g| *g < 255);
        if self.mode == TRAVEL && self.leader == Some(slot) {
            if self.goal != job { self.claims = 0; }
            self.goal = job;
        }
        if self.mode == TRAVEL && job.is_some() && self.goal == job {
            self.claims |= 1 << slot;
        } else {
            self.claims &= !(1 << slot);
        }
    }
    pub fn fresh(self, round: u32, alive: &[bool]) -> bool {
        self.leader.map_or(false, |s| alive.get(s).copied().unwrap_or(false))
            && round >= self.round as u32 && round - self.round as u32 <= 3
    }
}
pub fn elect(packet: Packet, alive: &[bool], priority: &[usize], round: u32) -> Option<usize> {
    if packet.fresh(round, alive) { return packet.leader; }
    priority.iter().copied().find(|s| Some(*s) != packet.leader && alive.get(*s).copied().unwrap_or(false))
        .or_else(|| priority.iter().copied().find(|s| alive.get(*s).copied().unwrap_or(false)))
}
fn distance(a: (i32, i32), b: (i32, i32)) -> i32 { (a.0-b.0).abs().max((a.1-b.1).abs()) }
// Regroup before the hard movement tether is reached, so escorts keep moving.
pub fn needs_regroup(here: (i32, i32), anchor: (i32, i32)) -> bool {
    distance(here, anchor) > 2
}
pub fn escort_tile_clear(tile: (i32, i32), altar: (i32, i32)) -> bool {
    distance(tile, altar) > 1
}
pub fn permits_step_with_radius(here: (i32, i32), next: (i32, i32), anchor: (i32, i32), radius: i32) -> bool {
    distance(next, anchor) <= distance(here, anchor).max(radius)
}
pub fn permits_step(here: (i32, i32), next: (i32, i32), anchor: (i32, i32)) -> bool {
    permits_step_with_radius(here, next, anchor, 3)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn round_trip_and_bit_isolation() {
        let mut p = Packet { leader: Some(5), pos: (49, 47), round: 2000, mode: TRAVEL,
            goal: Some(254), claims: 63, focus: Some(4), gates: 3 };
        assert_eq!(Packet::decode(p.encode()), p);
        p.publish(2, (6, 8), 2001, BANK);
        assert_eq!(p.goal, None); assert_eq!(p.claims, 0);
        assert_eq!(p.focus, Some(4)); assert_eq!(p.gates, 3);
        assert_eq!(Packet::decode(p.encode()), p);
        p.focus = None; p.gates = 1;
        assert_eq!(Packet::decode(p.encode()).mode, BANK);
        assert_eq!(Packet::decode([0; 8]), Packet::default());
    }
    #[test]
    fn shared_claim_changes_do_not_leave_stale_followers() {
        let mut p = Packet::default(); p.publish(2, (4, 4), 10, TRAVEL);
        p.set_claim(2, Some(8)); p.set_claim(1, Some(8));
        assert_eq!(p.claim_of(1), Some(8)); assert_eq!(p.claim_of(2), Some(8));
        p.set_claim(2, Some(9)); assert_eq!(p.claim_of(1), None);
        p.set_claim(1, Some(8)); assert_eq!(p.goal, Some(9)); assert_eq!(p.claim_of(1), None);
        p.publish(1, (5, 4), 11, HOME); p.set_claim(1, Some(9));
        assert_eq!(p.claim_of(1), None);
        p.goal = Some(255); assert_eq!(Packet::decode(p.encode()).goal, None);
    }
    #[test]
    fn leadership_survives_respawn_but_not_death_or_stale_heartbeat() {
        let mut p = Packet::default(); p.publish(1, (2, 2), 100, TRAVEL);
        assert_eq!(elect(p, &[true,true,true], &[0,1,2], 103), Some(1));
        assert_eq!(elect(p, &[true,false,true], &[0,1,2], 103), Some(0));
        assert_eq!(elect(p, &[true,true,true], &[0,1,2], 104), Some(0));
        assert_eq!(elect(p, &[false,false,false], &[0,1,2], 103), None);
        assert!(!p.fresh(99, &[true,true,true]));
    }
    #[test]
    fn tether_allows_recovery_without_moving_further_away() {
        assert!(!permits_step((3,0), (4,0), (0,0)));
        assert!(permits_step((3,0), (3,1), (0,0)));
        assert!(permits_step((7,0), (6,0), (0,0)));
        assert!(!permits_step((7,0), (8,0), (0,0)));
    }
    #[test]
    fn empty_handed_escort_leaves_room_for_banking_progress() {
        let mut leader = (3, 0);
        let mut escort = (0, 0);
        assert!(!permits_step(leader, (4,0), escort));
        assert!(!needs_regroup((2,0), (0,0)));
        for _ in 0..5 {
            assert!(needs_regroup(escort, leader));
            let next_escort = (escort.0 + 1, 0);
            assert!(permits_step(escort, next_escort, leader));
            escort = next_escort;
            let next_leader = (leader.0 + 1, 0);
            assert!(permits_step(leader, next_leader, escort));
            leader = next_leader;
        }
        assert_eq!(leader, (8,0));
    }
    #[test]
    fn empty_escorts_leave_the_altar_approach_open() {
        let altar = (13,26);
        let banker = (15,27);
        let blocked = [(14,26),(14,27)];
        let clear = [(15,25),(15,28)];
        for (old,new) in blocked.into_iter().zip(clear) {
            assert!(!escort_tile_clear(old,altar));
            assert!(escort_tile_clear(new,altar));
            assert!(permits_step(old,new,banker));
        }
        let approach = (14,26);
        assert!(!clear.contains(&approach));
        for ally in clear.into_iter().chain([(15,26),(17,28)]) {
            assert!(permits_step(banker,approach,ally));
        }
    }
    #[test]
    fn obstruction_margin_is_bounded_and_preserves_recovery() {
        assert!(!permits_step((3,0),(4,0),(0,0)));
        assert!(permits_step_with_radius((3,0),(4,0),(0,0),4));
        assert!(!permits_step_with_radius((4,0),(5,0),(0,0),4));
        assert!(permits_step_with_radius((7,0),(6,0),(0,0),4));
        assert!(!permits_step_with_radius((7,0),(8,0),(0,0),4));
    }
}
