/// Baraja un slice in situ con el algoritmo de Fisher–Yates. `O(n)`.
pub fn shuffle<T>(&mut self, items: &mut [T]) {
    for i in (1..items.len()).rev() {
        let j = self.next_usize(i + 1);
        items.swap(i, j);
    }
}
