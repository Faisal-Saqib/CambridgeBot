pub fn flags(b: u8) -> u8 { b & 3 }
pub fn leader(b: u8) -> Option<usize> { let x=(b>>2)&7; (1..=6).contains(&x).then(||x as usize-1) }
pub fn sequence(b: u8) -> u8 { b>>5 }
pub fn with_flags(b:u8,f:u8)->u8 { (b & !3) | (f & 3) }
pub fn with_leader(b:u8,slot:Option<usize>)->u8 {
    let x=slot.filter(|s|*s<6).map_or(0,|s|(s+1) as u8);
    (b & !28) | (x<<2)
}
pub fn pulse(b:u8)->u8 { (b & 31) | ((sequence(b)%7+1)<<5) }
pub fn active(seen:Option<u32>,round:u32)->bool { seen.map_or(false,|s|round>=s && round-s<=20) }
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn fields_do_not_clobber_each_other() {
        let b=pulse(with_flags(with_leader(0,Some(5)),3));
        assert_eq!(flags(b),3);assert_eq!(leader(b),Some(5));assert_eq!(sequence(b),1);
        let c=with_flags(b,0);assert_eq!(leader(c),Some(5));assert_eq!(sequence(c),1);
        let d=with_leader(c,None);assert_eq!(leader(d),None);assert_eq!(sequence(d),1);
        assert_eq!(leader(with_leader(d,Some(6))),None);
    }
    #[test] fn alert_generation_wraps_without_losing_control_fields() {
        let mut b=with_flags(with_leader(0,Some(2)),2);
        for i in 0..30 { b=pulse(b);assert_eq!(sequence(b),(i%7+1) as u8);assert_eq!(leader(b),Some(2));assert_eq!(flags(b),2); }
    }
    #[test] fn alert_is_absent_initially_and_expires() {
        assert!(!active(None,1));assert!(active(Some(10),30));assert!(!active(Some(10),31));assert!(!active(Some(10),9));
    }
}