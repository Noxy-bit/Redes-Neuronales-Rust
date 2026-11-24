fn parsear(args: &[String]) -> Result<Option<Opciones>, String> {
    let mut op = Opciones::default();
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "-h" | "--help" => return Ok(None),
            "--all" => op.todo = true,
            "--exp1" | "--exp2" | "--exp3" | "--escritorio" | "--bench" => {
                activar(&mut op, &a[2..])?
            }
            "--experiment" => activar(&mut op, it.next().ok_or("falta valor para --experiment")?)?,
            "--export" => {
                op.dir = Some(PathBuf::from(it.next().ok_or("falta valor para --export")?))
            }
            "--seed" => {
                let v = it.next().ok_or("falta valor para --seed")?;
                op.semilla = Some(v.parse().map_err(|_| format!("semilla inválida: {v}"))?);
            }
            otro => return Err(format!("opción desconocida: {otro}")),
        }
    }
    if op.todo {
        op.exp1 = true;
        op.exp2 = true;
        op.exp3 = true;
        op.escritorio = true;
        op.bench = true;
    }
    if !(op.exp1 || op.exp2 || op.exp3 || op.escritorio || op.bench) {
        return Ok(None);
    }
    Ok(Some(op))
}
