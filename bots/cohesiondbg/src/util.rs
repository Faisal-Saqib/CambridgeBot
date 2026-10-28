use cambc::{Champion, Vec2};

/// Debug logging into the replay; compiled out when DEBUG is false.
pub const DEBUG: bool = true;

#[macro_export]
macro_rules! log {
    ($self:expr, $($arg:tt)*) => {
        if $crate::util::DEBUG {
            println!("r{} {:?}@{},{} {}", $self.round, $self.kind, $self.pos.x, $self.pos.y, format!($($arg)*));
        }
    };
}

pub const DIRS: [Vec2; 8] = [
    Vec2::NORTH,
    Vec2::NORTH_EAST,
    Vec2::EAST,
    Vec2::SOUTH_EAST,
    Vec2::SOUTH,
    Vec2::SOUTH_WEST,
    Vec2::WEST,
    Vec2::NORTH_WEST,
];

pub fn me() -> &'static Champion {
    cambc::self_champion().ok().flatten().expect("gameplay champion")
}

pub fn cheb(a: Vec2, b: Vec2) -> i32 {
    a.chebyshev_distance(b) as i32
}

pub fn fuel() -> u64 {
    cambc::fuel_remaining().unwrap_or(0)
}
