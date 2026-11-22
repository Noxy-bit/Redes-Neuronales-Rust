impl LossFn for Mse {
    fn loss(&self, prediction: &Vector, target: &Vector) -> MathResult<f64> {
        validar(prediction, target, "MSE")?;
        let diff = prediction.sub(target)?;
        Ok(diff.dot(&diff)? / prediction.len() as f64)
    }

    fn derivative(&self, prediction: &Vector, target: &Vector) -> MathResult<Vector> {
        validar(prediction, target, "derivada de MSE")?;
        Ok(prediction.sub(target)?.scale(2.0 / prediction.len() as f64))
    }
}
