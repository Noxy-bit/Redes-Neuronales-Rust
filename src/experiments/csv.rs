//! Escritor CSV mínimo (sin dependencias externas).

use std::fs::{self, File};
use std::io::{self, BufWriter, Write};
use std::path::Path;

/// Escritor de archivos CSV con separador `,` y vectores serializados con `;`.
///
/// Los números se escriben con la representación decimal más corta que
/// reconstruye exactamente el `f64` (formato `Display` de Rust), por lo que
/// los valores exportados son idénticos a los calculados en memoria.
pub struct CsvWriter {
    writer: BufWriter<File>,
    columnas: usize,
}

impl CsvWriter {
    /// Crea (o sobrescribe) el archivo, crea los directorios padres y escribe
    /// la fila de encabezados. `O(c)` con `c` columnas.
    pub fn create(path: &Path, header: &[&str]) -> io::Result<Self> {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        let mut writer = BufWriter::new(File::create(path)?);
        writeln!(writer, "{}", header.join(","))?;
        Ok(Self {
            writer,
            columnas: header.len(),
        })
    }

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

    /// Vacía el búfer al disco.
    pub fn finish(mut self) -> io::Result<()> {
        self.writer.flush()
    }
}

/// Formatea un `f64` con la representación exacta más corta.
pub fn num(x: f64) -> String {
    format!("{x}")
}

/// Serializa un slice de `f64` como `v1;v2;…;vn` (apto para una celda CSV).
pub fn lista(v: &[f64]) -> String {
    v.iter().map(|&x| num(x)).collect::<Vec<_>>().join(";")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn escribe_y_valida_columnas() {
        let dir = crate::experiments::directorio_temporal("csv");
        let path = dir.join("sub").join("t.csv");
        let mut w = CsvWriter::create(&path, &["a", "b"]).unwrap();
        w.write_row(&[num(1.5), lista(&[0.1, 2.0])]).unwrap();
        assert!(w.write_row(&[num(1.0)]).is_err());
        w.finish().unwrap();
        let s = fs::read_to_string(&path).unwrap();
        assert_eq!(s, "a,b\n1.5,0.1;2\n");
        assert_eq!(num(0.1 + 0.2), "0.30000000000000004");
    }
}
