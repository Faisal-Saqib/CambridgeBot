// Team shared memory (8 bytes, readable and writable by every teammate):
//   bytes 0..6  claim per ally slot: camp group index + 1, or 0 for none
//   byte 6      focus: index + 1 of the enemy champion the team is hitting
//   byte 7      gate flags (bits 0-1: bit 0 assault on, bit 1 gate camp dead),
//               support-leader slot + 1 (bits 2-4), alert generation (bits 5-7)
use crate::guard_protocol as control;
use cambc::Result;

pub const SLOTS: usize = 6;
pub const GATE_ASSAULT: u8 = 1;
pub const GATE_OPEN: u8 = 2;

#[derive(Clone, Copy, Default)]
pub struct Comm {
    pub bytes: [u8; 8],
}

fn mem() -> &'static cambc::SharedMemory {
    cambc::shared_memory()
}

fn enc(g: Option<usize>) -> u8 {
    g.map_or(0, |g| (g + 1).min(255) as u8)
}

fn dec(v: u8) -> Option<usize> {
    (v != 0).then(|| v as usize - 1)
}

impl Comm {
    pub fn read() -> Result<Self> {
        let mut bytes = [0u8; 8];
        mem().read(0, &mut bytes)?;
        Ok(Self { bytes })
    }

    fn put(&mut self, i: usize, v: u8) -> Result<()> {
        if self.bytes[i] != v {
            self.bytes[i] = v;
            mem().set(i, v)?;
        }
        Ok(())
    }

    pub fn claim_of(&self, slot: usize) -> Option<usize> {
        if slot >= SLOTS {
            return None;
        }
        dec(self.bytes[slot])
    }

    pub fn set_claim(&mut self, slot: usize, group: Option<usize>) -> Result<()> {
        if slot >= SLOTS {
            return Ok(());
        }
        self.put(slot, enc(group))
    }

    pub fn focus(&self) -> Option<usize> {
        dec(self.bytes[6])
    }

    pub fn gate_flags(&self) -> u8 {
        control::flags(self.bytes[7])
    }

    pub fn set_gate_flags(&mut self, v: u8) -> Result<()> {
        let b = mem().get(7)?;
        self.bytes[7] = b;
        self.put(7, control::with_flags(b, v))
    }

    pub fn support_leader(&self) -> Option<usize> {
        control::leader(self.bytes[7])
    }

    pub fn alert_sequence(&self) -> u8 {
        control::sequence(self.bytes[7])
    }

    pub fn set_support_leader(&mut self, slot: Option<usize>) -> Result<()> {
        let b = mem().get(7)?;
        self.bytes[7] = b;
        self.put(7, control::with_leader(b, slot))
    }

    pub fn pulse_alert(&mut self) -> Result<()> {
        let b = mem().get(7)?;
        self.bytes[7] = b;
        self.put(7, control::pulse(b))
    }

    pub fn set_focus(&mut self, enemy: Option<usize>) -> Result<()> {
        self.put(6, enc(enemy))
    }
}
