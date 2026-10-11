param([ValidateSet('check','test','build','standalone')][string]$Action = 'build',
    [string]$MsysRoot = 'C:/msys64')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
# A instalação local é opcional; uma ferramenta Rust normal no PATH também funciona.
if (!$env:CI -and (Test-Path '../.build-tools/cargo/bin/cargo.exe')) {
    $env:RUSTUP_HOME = Join-Path (Get-Location) '../.build-tools/rustup'
    $env:CARGO_HOME = Join-Path (Get-Location) '../.build-tools/cargo'
    $env:PATH = "$env:CARGO_HOME/bin;$env:PATH"
}
if (!$env:CI -and (Test-Path '../.build-tools/python/bin/ninja.exe')) {
    $env:PATH = "$(Join-Path (Get-Location) '../.build-tools/python/bin');$env:PATH"
    $env:LIBCLANG_PATH = Join-Path (Get-Location) '../.build-tools/python/clang/native'
}
if (Test-Path (Join-Path $MsysRoot 'ucrt64/bin/gcc.exe')) {
    $env:PATH = "$MsysRoot/ucrt64/bin;$MsysRoot/usr/bin;$env:PATH"
    $env:CC = 'gcc'
    $env:CXX = 'g++'
    # O driver C++ aplica -static-libstdc++ também à biblioteca pedida pelo Dynarmic.
    $env:CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER = 'g++'
    $env:CMAKE_TOOLCHAIN_FILE = Join-Path $PSScriptRoot 'scripts/windows-gnu.cmake'
    $gccIncludes = (& gcc -print-file-name=include).Trim()
    $env:BINDGEN_EXTRA_CLANG_ARGS = "--target=x86_64-w64-windows-gnu -isystem $gccIncludes -isystem $MsysRoot/ucrt64/include"
}
if (!$env:LIBCLANG_PATH -and (Test-Path "$MsysRoot/ucrt64/bin/libclang.dll")) {
    $env:LIBCLANG_PATH = "$MsysRoot/ucrt64/bin"
}
$env:CMAKE_GENERATOR = 'Ninja'
switch ($Action) {
    'check' { cargo check --locked -p zeebx-libretro }
    'test' { cargo test --release --locked -p zeebx-libretro -- --test-threads=2 }
    'build' {
        if ((& rustc -vV) -match 'host: x86_64-pc-windows-gnu') {
            $env:CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER = 'g++'
            # Rust usa -nodefaultlibs e pede -lstdc++ explicitamente. Dar prioridade
            # aos arquivos .a evita que o linker escolha os importadores .dll.a.
            $runtimeDirectory = Join-Path (Get-Location) 'target/static-runtime'
            New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
            foreach ($library in @('libstdc++.a', 'libpthread.a')) {
                $sourceLibrary = (& g++ "-print-file-name=$library").Trim()
                if (!(Test-Path -LiteralPath $sourceLibrary)) { throw "Biblioteca estatica ausente: $library" }
                Copy-Item -LiteralPath $sourceLibrary -Destination (Join-Path $runtimeDirectory $library) -Force
            }
            # Símbolos internos não são necessários na entrega; os exports da ABI permanecem.
            cargo rustc --locked --release -p zeebx-libretro -- -L "native=$runtimeDirectory" -C link-arg=-static-libgcc -C strip=symbols
        } else {
            cargo build --locked --release -p zeebx-libretro
        }
    }
    'standalone' { cargo check --locked -p zeebx-standalone-egui }
}
exit $LASTEXITCODE
