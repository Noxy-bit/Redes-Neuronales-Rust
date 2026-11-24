/// Escribe una fila. Error `InvalidInput` si la cantidad de campos no
/// coincide con la de encabezados. `O(c)`.
pub fn write_row(&mut self, fields: &[String]) -> io::Result<()> {
    if fields.len() != self.columnas {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            format!(
                "fila con {} campos; se esperaban {}",
                fields.len(),
                self.columnas
            ),
        ));
    }
    writeln!(self.writer, "{}", fields.join(","))
}
