pub fn multiply(&self, other: &Matrix<T>) -> Matrix<T> {
    assert_eq!(
        self.columns, other.rows,
        "Columns of the first matrix must equal rows of the second matrix"
    );

    let mut data: Vec<T> = Vec::new();

    for i in 0..self.rows {
        for k in 0..other.columns {
            let mut sum = T::default();

            for j in 0..self.columns {
                let a = self.data[i * self.columns + j];
                let b = other.data[j * other.columns + k];

                sum = sum + (a * b);
            }

            data.push(sum);
        }
    }

    Matrix::new(self.rows, other.columns, data)
}
