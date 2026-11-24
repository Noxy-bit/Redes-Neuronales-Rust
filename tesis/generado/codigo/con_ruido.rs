/// Invierte `k` píxeles distintos elegidos con `rng` (Fisher–Yates parcial).
pub fn con_ruido(base: &Vector, k: usize, rng: &mut Rng) -> Vector {
    let mut idx: Vec<usize> = (0..base.len()).collect();
    rng.shuffle(&mut idx);
    let mut v = base.clone();
    for &i in idx.iter().take(k) {
        v.as_mut_slice()[i] = 1.0 - v.as_slice()[i];
    }
    v
}
