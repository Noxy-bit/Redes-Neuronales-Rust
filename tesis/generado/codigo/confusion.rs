/// Matriz de confusión `C[real][predicha]` por `argmax`. `O(N·P)`.
pub fn matriz_confusion(red: &Network, muestras: &[Muestra]) -> MathResult<[[usize; 5]; 5]> {
    let mut c = [[0usize; 5]; 5];
    for m in muestras {
        let pred = red.predict(&m.pixeles)?.argmax().unwrap_or(0);
        c[m.clase][pred] += 1;
    }
    Ok(c)
}
