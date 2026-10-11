//! Lançador do EmuVR; o carregamento do pacote continua a cargo do core original.
use serde::Deserialize;
use std::path::{Path, PathBuf};

#[derive(Default, Deserialize)]
#[serde(default, deny_unknown_fields)]
struct Launcher {
    z_wheel: Option<PathBuf>,
    games: Option<PathBuf>,
}

pub struct Content {
    pub entry: PathBuf,
    pub games: Option<PathBuf>,
}

fn relative(base: &Path, path: PathBuf) -> PathBuf {
    if path.is_absolute() {
        path
    } else {
        base.join(path)
    }
}

pub fn resolve(path: &Path, system: Option<&Path>) -> Result<Option<Content>, String> {
    if !path
        .extension()
        .is_some_and(|s| s.eq_ignore_ascii_case("zeebo"))
    {
        return Ok(None);
    }
    let text = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
    let text = text.trim_start_matches('\u{feff}').trim();
    let launcher: Launcher = if text.is_empty() {
        Launcher::default()
    } else {
        serde_json::from_str(text).map_err(|e| format!("Lançador .zeebo inválido: {e}"))?
    };
    let base = path.parent().unwrap_or(Path::new("."));
    let candidate = match launcher.z_wheel {
        Some(p) => relative(base, p),
        None => system
            .ok_or("Informe z_wheel no .zeebo ou configure system_directory")?
            .join("zeebx/Z-Wheel.zip"),
    };
    let entry = zeebx::library::z_wheel_em(&candidate)
        .ok_or_else(|| format!("Z-Wheel ausente ou inválido: {}", candidate.display()))?;
    let games = match launcher.games {
        Some(p) => {
            let dir = relative(base, p);
            if !dir.is_dir() {
                return Err(format!("Pasta de jogos ausente: {}", dir.display()));
            }
            Some(dir)
        }
        None => system.map(|p| p.join("zeebx/games")),
    };
    Ok(Some(Content { entry, games }))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn launcher_paths_and_unknown_fields() {
        let l: Launcher =
            serde_json::from_str(r#"{"z_wheel":"../Z-Wheel.zip","games":".."}"#).unwrap();
        assert_eq!(
            relative(Path::new("gpu"), l.games.unwrap()),
            Path::new("gpu/..")
        );
        assert!(serde_json::from_str::<Launcher>(r#"{"../games":"."}"#).is_err());
        assert!(resolve(Path::new("game.zip"), None).unwrap().is_none());
    }
}
