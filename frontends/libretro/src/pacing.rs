//! Limita o avanço virtual à cadência de 60 Hz anunciada pelo frontend.
#[derive(Default)]
pub struct Pacing {
    credit: i64,
    last: u32,
}
impl Pacing {
    pub fn reset(&mut self, now: u32) {
        self.credit = 0;
        self.last = now;
    }
    pub fn advance(&mut self, now: u32) -> bool {
        // Unidades de 1/60 ms: não perde a fração de 16,666... ms por chamada.
        self.credit += 1000 - i64::from(now.wrapping_sub(self.last)) * 60;
        self.last = now;
        self.credit > 0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn compensates_long_steps_without_wall_clock() {
        let mut pacing = Pacing::default();
        let mut now = u32::MAX - 500;
        let start = now;
        pacing.reset(now);
        for _ in 0..600 {
            if pacing.advance(now) { now = now.wrapping_add(49); }
        }
        assert!((10000..10049).contains(&now.wrapping_sub(start)));
        pacing.reset(now);
        assert!(pacing.advance(now));
    }
}
