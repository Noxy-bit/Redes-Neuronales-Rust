impl ActivationFn for ReLU {
    fn activate(&self, z: f64) -> f64 {
        z.max(0.0)
    }

    fn derivative(&self, z: f64) -> f64 {
        if z > 0.0 { 1.0 } else { 0.0 }
    }

    fn name(&self) -> &'static str {
        "ReLU"
    }
}
