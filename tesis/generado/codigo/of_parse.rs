fn parse_vowel(value: &str) -> Result<usize, &'static str> {
    if value.chars().count() != 1 {
        return Err("pasa una sola vocal: a, e, i, o o u");
    }
    match value.to_ascii_uppercase().as_str() {
        "A" => Ok(0),
        "E" => Ok(1),
        "I" => Ok(2),
        "O" => Ok(3),
        "U" => Ok(4),
        _ => Err("la entrada debe ser una vocal: a, e, i, o o u"),
    }
}
