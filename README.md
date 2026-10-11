# Zeebx EmuVR — core libretro

Adaptação comunitária do [Zeebx](https://github.com/ZeebxTeam/zeebx-emu), baseada na versão **0.4.2**, para Windows x64, EmuVR e RetroArch 1.7.5. Este fork não é uma release oficial da ZeebxTeam. O motor de emulação e suas correções são do projeto original.

## Instalação

1. Copie `zeebx_libretro.dll` para `RetroArch/cores/`.
2. Copie `zeebx_libretro.info` para `RetroArch/info/`.
3. Abra um jogo ZIP, 7z ou MOD, ou um lançador `.zeebo`.

O pacote não inclui jogos, firmware nem Z-Wheel. Você precisa fornecer esses arquivos.

## Z-Wheel e lançadores .zeebo

Coloque o exemplo `examples/Z-Wheel.zeebo` junto de `Z-Wheel.zip` e dos jogos. O arquivo contém:

```json
{
  "z_wheel": "Z-Wheel.zip",
  "games": "."
}
```

Os caminhos são relativos ao arquivo `.zeebo`. Para um lançador numa subpasta, com os conteúdos na pasta acima:

```json
{
  "z_wheel": "../Z-Wheel.zip",
  "games": ".."
}
```

O campo `games` indica a biblioteca da Z-Wheel; não é uma chave com o nome da pasta. Arquivo vazio ou `{}` usa a localização padrão `system/zeebx/Z-Wheel.zip` e `system/zeebx/games` do frontend.

## Adaptações e limites

- Reconhecimento de `.zeebo`, caminhos relativos e catálogo da Z-Wheel.
- Apresentação completa das camadas 2D/3D e preservação da tela de aguarde na troca de aplicativo.
- Compensação da cadência de 60 Hz anunciada ao frontend.
- Mapeamento anterior do port, com Start e Select como HOME; sem instrumentação de testes de controles.
- Cache das opções de espelhamento do direcional no analógico.
- Runtimes GNU estáticos e símbolos internos removidos na DLL distribuída.

O comportamento dos botões durante o jogo pode divergir das instruções exibidas por alguns títulos; não há remapeamento automático por jogo. O netplay do EmuVR não está validado e apresentou crescimento excessivo de memória em testes anteriores. A compatibilidade de save states entre versões não é garantida.

A validação local da 0.4.2 incluiu ABI, testes do frontend, splash e execução OpenGL de Z-Wheel, Double Dragon e Boia Cross. Isso não substitui testes manuais de cada jogo no RetroArch/EmuVR.

## Compilar no Windows

Instale Rust com a ferramenta `stable-x86_64-pc-windows-gnu`, Python 3 e MSYS2 UCRT64. Pelo terminal UCRT64, instale:

```sh
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-ninja mingw-w64-ucrt-x86_64-clang
```

No PowerShell, na raiz deste repositório:

```powershell
rustup toolchain install stable-x86_64-pc-windows-gnu --profile minimal
$env:RUSTUP_TOOLCHAIN = 'stable-x86_64-pc-windows-gnu'
./build-core.ps1 -Action build
./build-core.ps1 -Action test
./scripts/package-core.ps1
```

Para MSYS2 fora de `C:/msys64`, passe `-MsysRoot 'caminho'` aos scripts. O ZIP fica em `dist/`. Não é necessário ter as versões anteriores do projeto. O suporte opcional às ferramentas locais da pasta pai existe somente para o ambiente de desenvolvimento original, fora do CI.

Os testes comuns não distribuem ROMs; testes condicionais que exigem conteúdo local são pulados quando ele não está configurado. `test-video.py` é um teste local de OpenGL e requer Pillow, Windows e ROM própria.

## Organização e créditos

- `src/`: motor oficial 0.4.2, preservado.
- `frontends/libretro/`: adaptações deste port; `content.rs`, `pacing.rs` e `presentation.rs` separam lançadores, cadência e apresentação.
- `scripts/`: compilação auxiliar, testes e empacotamento autossuficientes.
- `examples/`: exemplo sem conteúdo do console.
- `UPDATE-EMUVR.md`: integração e validação local.
- `README-UPSTREAM.md`: apresentação original e créditos da ZeebxTeam.
- `docs/upstream-workflows/`: workflows originais arquivados; não executam neste fork.

Os demais frontends e documentos do upstream foram preservados para manter a árvore de origem e o workspace; o workflow deste fork compila apenas libretro.

Código Zeebx: GPL-2.0-or-later; binários distribuídos sob GPLv3 conforme as dependências. Consulte `LICENSE`, `LICENSE-GPL3` e `THIRD-PARTY-NOTICES.txt`. Ao distribuir uma DLL modificada, disponibilize também o código-fonte correspondente e as instruções de compilação. Os créditos originais foram preservados.
