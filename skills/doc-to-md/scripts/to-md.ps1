<#
  to-md.ps1 -- convert a document to Markdown with MinerU (portable wrapper).

  Examples:
    powershell -NoProfile -ExecutionPolicy Bypass -File to-md.ps1 -InputPath "paper.pdf"
    powershell -NoProfile -ExecutionPolicy Bypass -File to-md.ps1 -InputPath "scan.pdf" -Pages "1-5,8" -Tier standard
    powershell -NoProfile -ExecutionPolicy Bypass -File to-md.ps1 -InputPath "doc.pdf" -Remote

  MinerU discovery order:
    -MineruExe  ->  $env:MINERU_EXE  ->  mineru on PATH  ->  current python's Scripts dir

  Requires MinerU 4.x:   pip install "mineru[core]"
  Local tiers need the parse server running:   mineru server start   (once per boot)
  Tiers: flash (offline, fast) | basic | standard | advanced (models download on first use)
  Env: MINERU_MODEL_SOURCE defaults to modelscope (CN mirror); set huggingface to switch.
  Note: -Pages applies to PDF inputs only; it is omitted automatically for other
  file types (MinerU rejects --pages for non-PDF files).

  NOTE FOR MAINTAINERS: keep this file pure ASCII. Windows PowerShell 5.1 reads a
  BOM-less UTF-8 .ps1 as ANSI/GBK and the script breaks on non-ASCII characters.
#>
param(
  [Parameter(Mandatory = $true)][string]$InputPath,
  [string]$OutFile = '',
  [string]$Pages = 'all',
  [string]$Tier = 'flash',
  [string]$MineruExe = '',
  [switch]$Remote
)

$ErrorActionPreference = 'Stop'

if (-not $env:MINERU_MODEL_SOURCE) { $env:MINERU_MODEL_SOURCE = 'modelscope' }

function Resolve-Mineru {
  param([string]$Explicit)
  if ($Explicit) {
    if (-not (Test-Path -LiteralPath $Explicit)) { throw ('-MineruExe not found: ' + $Explicit) }
    return (Get-Item -LiteralPath $Explicit).FullName
  }
  if ($env:MINERU_EXE -and (Test-Path -LiteralPath $env:MINERU_EXE)) {
    return (Get-Item -LiteralPath $env:MINERU_EXE).FullName
  }
  $cmd = Get-Command mineru -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $py = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
  if ($py) {
    $probe = & $py.Source -c "import sysconfig,os;d=sysconfig.get_path('scripts');print(os.path.join(d,'mineru.exe' if os.name=='nt' else 'mineru'))" 2>$null
    if ($probe -and (Test-Path -LiteralPath $probe)) { return $probe }
  }
  throw 'mineru not found. Install: pip install "mineru[core]"  |  pass -MineruExe <path>  |  set MINERU_EXE.'
}

$src = Get-Item -LiteralPath $InputPath
if (-not $OutFile) { $OutFile = Join-Path $src.DirectoryName ($src.BaseName + '_md.md') }

$exe = Resolve-Mineru -Explicit $MineruExe

$tierShown = $Tier
if ($Remote) { $tierShown = $Tier + ' (remote via mineru.net)' }
$isPdf = ($src.Extension.ToLowerInvariant() -eq '.pdf')
$pagesShown = $Pages
if (-not $PSBoundParameters.ContainsKey('Pages')) {
  if ($isPdf) { $pagesShown = 'all (pdf default)' } else { $pagesShown = 'n/a (non-PDF: full document)' }
}
Write-Output ('[to-md] input  : ' + $src.FullName)
Write-Output ('[to-md] output : ' + $OutFile)
Write-Output ('[to-md] pages  : ' + $pagesShown + ' | tier: ' + $tierShown + ' | models: ' + $env:MINERU_MODEL_SOURCE)

# --pages is PDF-only in MinerU; passing it for other file types fails the parse.
$mineruArgs = @('parse', $src.FullName)
if ($PSBoundParameters.ContainsKey('Pages')) {
  $mineruArgs += @('--pages', $Pages)
} elseif ($isPdf) {
  $mineruArgs += @('--pages', 'all')
}
$mineruArgs += @('--tier', $Tier, '--wait', '600', '-o', $OutFile)
if ($Remote) { $mineruArgs += '--remote' }

& $exe @mineruArgs
$code = $LASTEXITCODE

if ($code -ne 0) {
  Write-Output ('[to-md] mineru exit code ' + $code)
  Write-Output '        - local tiers need the parse server:  mineru server start'
  Write-Output '        - first standard/advanced run downloads models (flash is offline)'
  Write-Output '        - if the error mentions xethub.hf.co (401): set model.source to modelscope in ~/.mineru/config.yaml, then restart the server'
  exit $code
}
if (Test-Path -LiteralPath $OutFile) {
  Write-Output ('[to-md] MD: ' + $OutFile)
} else {
  Write-Output '[to-md] warning: output file was not created (see mineru output above)'
  exit 2
}
