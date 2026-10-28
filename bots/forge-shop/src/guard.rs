use crate::bot::Bot;
use crate::guard_protocol;
use crate::util::cheb;
use cambc::{ChampionType as C, Result};
impl Bot {
    pub fn guard_active(&self)->bool { guard_protocol::active(self.guard_seen,self.round) }
    fn guard_valid_leader(&self,s:usize)->bool {
        self.alive_flags.get(s).copied().unwrap_or(false)
            && self.comm.claim_of(s)!=Some(self.kb.spawn_field())
    }
    pub fn guard_update(&mut self)->Result<()> {
        let seq=self.comm.alert_sequence();
        if seq!=0 && seq!=self.guard_sequence { self.guard_seen=Some(self.round); }
        self.guard_sequence=seq;
        let danger=self.enemies.iter().any(|e| !e.on_spawn || cheb(e.pos,self.pos)<=e.range)
            || self.recent_deaths()>0;
        if danger {
            self.guard_seen=Some(self.round);
            if self.round%4==self.slot as u32%4 {
                self.comm.pulse_alert()?; self.guard_sequence=self.comm.alert_sequence();
            }
        }
        if !self.guard_active() { return Ok(()); }
        let banking=(0..self.team.len()).find(|&s| self.guard_valid_leader(s)
            && self.comm.claim_of(s).map_or(false,|g|g>=self.kb.groups.len() && g<self.kb.spawn_field()));
        let current=self.comm.support_leader().filter(|&s|self.guard_valid_leader(s));
        let chosen=banking.or(current).or_else(||(0..self.team.len()).filter(|&s|self.guard_valid_leader(s)).min_by_key(|&s| {
            (match self.team[s].champion_name().ok() { Some(C::Ryth)=>0,Some(C::Marcella)=>1,Some(C::VesperVale)=>2,Some(C::Tavi)=>3,_=>4 },s)
        }));
        if chosen!=self.comm.support_leader() { self.comm.set_support_leader(chosen)?; }
        Ok(())
    }
    pub fn guard_goal(&self)->Option<usize> {
        if !self.guard_active() { return None; }
        let s=self.comm.support_leader()?;
        if s==self.slot || !self.guard_valid_leader(s) { return None; }
        self.comm.claim_of(s).filter(|g|*g<self.kb.spawn_field())
    }
    pub fn guard_job_score(&self,g:usize,score:f32)->f32 {
        let Some(goal)=self.guard_goal() else { return score; };
        let target=if goal<self.kb.groups.len() { self.kb.groups[goal].center }
            else { self.kb.altars[goal-self.kb.groups.len()] };
        if g==goal { score*2.0 }
        else if cheb(self.kb.groups[g].center,target)>8 { score*0.25 }
        else { score }
    }
    pub fn guard_regroup(&mut self)->Result<bool> {
        if !self.guard_active() || self.healing || self.capture_on.is_some() || self.should_bank()? { return Ok(false); }
        let Some(s)=self.comm.support_leader().filter(|&s|self.guard_valid_leader(s)) else {return Ok(false)};
        if s==self.slot { return Ok(false); }
        let goal=self.guard_goal();
        if self.gems==0 {
            if let Some(g)=goal.filter(|g|*g>=self.kb.groups.len()) {
                let altar=self.kb.altars[g-self.kb.groups.len()];
                if cheb(self.pos,altar)<=1 {
                    self.step_by(|_,p|if cheb(p,altar)>1 {0.0}else{1.0})?;
                    return Ok(false);
                }
            }
        }
        if self.enemies.iter().any(|e|!e.on_spawn && cheb(e.pos,self.pos)<=e.range.max(self.range)+1) { return Ok(false); }
        if let Some(pos)=self.allies.iter().find(|a|a.ch==self.team[s]).map(|a|a.pos) {
            if cheb(pos,self.pos)<=3 { return Ok(false); }
            let moved=self.step_by(|_,p|cheb(p,pos) as f32)?;
            if !moved { return self.step_to(pos); }
            return Ok(true);
        }
        if let Some(g)=goal {
            let moved=self.step_field(g)?;
            if !moved && g<self.kb.groups.len() { return self.step_to(self.kb.groups[g].center); }
            return Ok(moved);
        }
        Ok(false)
    }
}