//! Generador pseudoaleatorio reproducible implementado en Rust puro.

/// Generador pseudoaleatorio **SplitMix64** (Steele, Lea y Flood, 2014).
///
/// Estado interno de 64 bits; cada llamada avanza el estado con la constante
/// áurea `0x9E3779B97F4A7C15` y aplica una función de mezcla biyectiva.
/// Con la misma semilla produce siempre la misma secuencia, lo que garantiza
/// la reproducibilidad exacta de la inicialización de pesos y de los datasets.
///
/// Complejidad: `O(1)` por número generado; memoria `O(1)`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Rng {
    state: u64,
}

impl Rng {
    /// Crea un generador a partir de una semilla fija.
    pub fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    /// Devuelve el siguiente entero pseudoaleatorio de 64 bits.
    ///
    /// `z ← (z ⊕ (z ≫ 30))·C₁; z ← (z ⊕ (z ≫ 27))·C₂; z ⊕ (z ≫ 31)`. `O(1)`.
    pub fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    /// Real uniforme en `[0, 1)` con 53 bits de precisión (mantisa de `f64`). `O(1)`.
    pub fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / (1u64 << 53) as f64)
    }

    /// Real uniforme en `[low, high)`: `low + (high − low)·u`, con `u ∈ [0, 1)`. `O(1)`.
    pub fn uniform(&mut self, low: f64, high: f64) -> f64 {
        low + (high - low) * self.next_f64()
    }

    /// Entero uniforme en `[0, n)`. Devuelve `0` si `n == 0`. `O(1)`.
    pub fn next_usize(&mut self, n: usize) -> usize {
        if n == 0 {
            return 0;
        }
        (self.next_f64() * n as f64) as usize % n
    }

    /// Baraja un slice in situ con el algoritmo de Fisher–Yates. `O(n)`.
    pub fn shuffle<T>(&mut self, items: &mut [T]) {
        for i in (1..items.len()).rev() {
            let j = self.next_usize(i + 1);
            items.swap(i, j);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn vector_de_referencia_splitmix64() {
        let mut rng = Rng::new(0);
        assert_eq!(rng.next_u64(), 0xE220_A839_7B1D_CDAF);
    }

    #[test]
    fn misma_semilla_misma_secuencia() {
        let mut a = Rng::new(42);
        let mut b = Rng::new(42);
        for _ in 0..100 {
            assert_eq!(a.next_u64(), b.next_u64());
        }
        let mut c = Rng::new(43);
        assert_ne!(Rng::new(42).next_u64(), c.next_u64());
    }

    #[test]
    fn rangos_uniformes() {
        let mut rng = Rng::new(7);
        let mut suma = 0.0;
        for _ in 0..10_000 {
            let u = rng.next_f64();
            assert!((0.0..1.0).contains(&u));
            let v = rng.uniform(-2.0, 3.0);
            assert!((-2.0..3.0).contains(&v));
            assert!(rng.next_usize(5) < 5);
            suma += u;
        }
        let media = suma / 10_000.0;
        assert!((media - 0.5).abs() < 0.02, "media = {media}");
        assert_eq!(rng.next_usize(0), 0);
    }

    #[test]
    fn shuffle_es_permutacion() {
        let mut rng = Rng::new(1);
        let mut v: Vec<usize> = (0..20).collect();
        rng.shuffle(&mut v);
        let mut ordenado = v.clone();
        ordenado.sort();
        assert_eq!(ordenado, (0..20).collect::<Vec<_>>());
        assert_ne!(v, (0..20).collect::<Vec<_>>());
    }
}
