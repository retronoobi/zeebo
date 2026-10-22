param([Parameter(Mandatory)][string]$MsysRoot,
      [Parameter(Mandatory)][string]$Destination)
$ErrorActionPreference = 'Stop'
# Algumas instalações de CI não trazem share/licenses. Mantemos cópias dos
# textos dos runtimes no repositório, sem depender de downloads no empacotamento.
foreach ($runtime in @('gcc-libs','libwinpthread')) {
    $installed = Join-Path $MsysRoot "ucrt64/share/licenses/$runtime"
    $bundled = Join-Path $PSScriptRoot "runtime-licenses/$runtime"
    $required = if ($runtime -eq 'gcc-libs') {
        @('COPYING3','COPYING.RUNTIME','COPYING.LIB','README')
    } else { @('COPYING') }
    $out = Join-Path $Destination "licenses/$runtime"
    New-Item -ItemType Directory -Path $out -Force | Out-Null
    foreach ($name in $required) {
        $source = Join-Path $installed $name
        if (!(Test-Path -LiteralPath $source -PathType Leaf)) {
            $source = Join-Path $bundled $name
            Write-Output "Licença $runtime/${name}: usando cópia do repositório."
        }
        if (!(Test-Path -LiteralPath $source -PathType Leaf) -or (Get-Item -LiteralPath $source).Length -eq 0) {
            throw "Licença ausente ou vazia: $source"
        }
        Copy-Item -LiteralPath $source -Destination (Join-Path $out $name)
    }
    # Inclui também avisos adicionais de uma instalação mais nova do MSYS2.
    if (Test-Path -LiteralPath $installed -PathType Container) {
        Get-ChildItem -LiteralPath $installed | Copy-Item -Destination $out -Recurse -Force
    }
}
