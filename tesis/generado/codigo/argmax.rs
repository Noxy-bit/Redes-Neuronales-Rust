/// Índice de la componente máxima (`argmaxᵢ vᵢ`); `None` si está vacío.
/// En caso de empate devuelve el primer índice. `O(n)`.
pub fn argmax(&self) -> Option<usize> {
    let mut best: Option<(usize, f64)> = None;
    for (i, &x) in self.data.iter().enumerate() {
        match best {
            Some((_, b)) if x <= b => {}
            _ => best = Some((i, x)),
        }
    }
    best.map(|(i, _)| i)
}
