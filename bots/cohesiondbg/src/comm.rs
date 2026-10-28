// 8 bytes: leader, x, y, shared objective, claimant bits,
// combat-focus/gate/mode bits, and a full u16 rally round.
use cambc::{Result, Vec2};
pub use crate::formation_protocol::SLOTS;
use crate::formation_protocol::Packet;
pub const GATE_ASSAULT: u8 = 1;
pub const GATE_OPEN: u8 = 2;
#[derive(Clone, Copy, Default)]
pub struct Comm { pub bytes: [u8; 8] }
impl Comm {
    pub fn read() -> Result<Self> {
        let mut bytes = [0; 8]; cambc::shared_memory().read(0, &mut bytes)?; Ok(Self { bytes })
    }
    pub fn packet(&self) -> Packet { Packet::decode(self.bytes) }
    fn replace(&mut self, p: Packet) -> Result<()> {
        let bytes = p.encode();
        if bytes != self.bytes { cambc::shared_memory().write(0, &bytes)?; self.bytes = bytes; }
        Ok(())
    }
    pub fn publish(&mut self, slot: usize, pos: Vec2, round: u32, mode: u8) -> Result<()> {
        let mut p = self.packet(); p.publish(slot, (pos.x,pos.y), round, mode); self.replace(p)
    }
    pub fn set_goal(&mut self, goal: Option<usize>) -> Result<()> {
        let mut p = self.packet(); p.goal = goal.filter(|g| *g < 255); p.claims = 0; self.replace(p)
    }
    pub fn claim_of(&self, slot: usize) -> Option<usize> { self.packet().claim_of(slot) }
    pub fn set_claim(&mut self, slot: usize, group: Option<usize>) -> Result<()> {
        let mut p = self.packet(); p.set_claim(slot, group); self.replace(p)
    }
    pub fn focus(&self) -> Option<usize> { self.packet().focus }
    pub fn set_focus(&mut self, enemy: Option<usize>) -> Result<()> {
        let mut p = self.packet(); p.focus = enemy.filter(|e| *e < SLOTS); self.replace(p)
    }
    pub fn gate_flags(&self) -> u8 { self.packet().gates }
    pub fn set_gate_flags(&mut self, flags: u8) -> Result<()> {
        let mut p = self.packet(); p.gates = flags & 3; self.replace(p)
    }
}
