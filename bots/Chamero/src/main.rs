// Dispatch draft and gameplay; errors are logged and the turn still yields.
mod bank;
mod bot;
mod comm;
mod draft;
mod farm;
mod gate;
mod fight;
mod guard;
mod guard_protocol;
mod heal;
mod kb;
mod nav;
mod shop;
mod util;

fn main() -> cambc::Result<()> {
    let mut bot: Option<bot::Bot> = None;
    loop {
        if cambc::is_draft() {
            if let Err(e) = draft::play() {
                println!("draft error: {e}");
            }
        } else {
            if bot.is_none() {
                match bot::Bot::new() {
                    Ok(b) => bot = Some(b),
                    Err(e) => println!("init error: {e}"),
                }
            }
            if let Some(b) = bot.as_mut() {
                if let Err(e) = b.turn() {
                    println!("r{} turn error: {e}", cambc::round_number().unwrap_or(0));
                }
            }
        }
        cambc::end_turn();
    }
}
