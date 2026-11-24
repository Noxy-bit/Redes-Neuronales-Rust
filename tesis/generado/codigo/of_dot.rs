pub fn dot(&self, other: &Vector<T>) -> T {
    assert_eq!(self.len(), other.len(), "Vector dimensions must match");

    let mut result = T::default();

    for i in 0..self.len() {
        result = result + self.data[i] * other.data[i];
    }

    result
}
