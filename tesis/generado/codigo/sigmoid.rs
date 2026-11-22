impl ActivationFn for Sigmoid {
    fn activate(&self, z: f64) -> f64 {
        if z >= 0.0 {
            1.0 / (1.0 + (-z).exp())
        } else {
            let e = z.exp();
            e / (1.0 + e)
        }
    }

    fn derivative(&self, z: f64) -> f64 {
        let s = self.activate(z);
        s * (1.0 - s)
    }

    fn name(&self) -> &'static str {
        "Sigmoid"
    }
}
