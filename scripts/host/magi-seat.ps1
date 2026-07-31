[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidateSet('seat-m','seat-d','seat-g')][string]$Seat,
  [Parameter(Mandatory=$true)][string]$Trial,
  [Parameter(Mandatory=$true)][string]$Brief,
  [Parameter(Mandatory=$true)][string]$EvidenceManifest,
  [Parameter(Mandatory=$true)][string]$AssignmentPlan,
  [string]$ProfileSource,
  [string]$TechnicalBase,
  [string]$TechnicalAgents,
  [string]$TechnicalConfig,
  [Parameter(Mandatory=$true)][string]$SeatConfig,
  [Parameter(Mandatory=$true)][string]$Policy,
  [string]$SecretFile,
  [string]$CredentialTarget,
  [switch]$Json
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$compose = Join-Path $repo 'container/compose.yml'
$trialPath = [IO.Path]::GetFullPath($Trial)
$briefPath = (Resolve-Path $Brief).Path
$evidenceManifestPath = (Resolve-Path $EvidenceManifest).Path
$assignmentPlanPath = (Resolve-Path $AssignmentPlan).Path
$seatConfigPath = (Resolve-Path $SeatConfig).Path
$policyPath = (Resolve-Path $Policy).Path
$temporarySecret = $null

function Resolve-TechnicalDefaults {
  if (-not $script:TechnicalBase) {
    $platform = if ($IsWindows) { 'win' } elseif ($IsMacOS) { 'mac' } else { 'linux' }
    if ($env:MAGI_TECHNICAL_BASE) { $script:TechnicalBase = $env:MAGI_TECHNICAL_BASE }
    else { $script:TechnicalBase = Join-Path $HOME "Private/agent-design/hermes/rules/$platform" }
  }
  if (-not $script:TechnicalAgents) { $script:TechnicalAgents = $env:MAGI_TECHNICAL_AGENTS }
  if (-not $script:TechnicalAgents) { throw 'Set -TechnicalAgents or MAGI_TECHNICAL_AGENTS.' }
  if (-not $script:TechnicalConfig) {
    if ($env:MAGI_TECHNICAL_CONFIG) { $script:TechnicalConfig = $env:MAGI_TECHNICAL_CONFIG }
    else {
      $profileHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME '.hermes/profiles/technical' }
      $script:TechnicalConfig = Join-Path $profileHome 'config.yaml'
    }
  }
}

try {
  $python = (Get-Command python -ErrorAction Stop).Source
  $profilePython = if ($env:MAGI_PROFILE_PYTHON) { $env:MAGI_PROFILE_PYTHON } else { $python }
  & $python (Join-Path $repo 'scripts/host/lib/seat_artifacts.py') validate brief $briefPath | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Original brief validation failed.' }
  & $python (Join-Path $repo 'scripts/host/lib/seat_artifacts.py') validate seat $seatConfigPath | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Seat configuration validation failed.' }
  & $python (Join-Path $repo 'scripts/host/lib/seat_artifacts.py') validate policy $policyPath --seat $seatConfigPath | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Seat policy validation failed.' }
  $seatConfigValue = Get-Content -Raw $seatConfigPath | ConvertFrom-Json
  if ($seatConfigValue.seat_id -ne $Seat) { throw 'Seat configuration does not match -Seat.' }

  if ($ProfileSource) {
    if ($TechnicalBase -or $TechnicalAgents -or $TechnicalConfig) { throw 'Choose -ProfileSource or technical composition, not both.' }
    $profilePath = (Resolve-Path $ProfileSource).Path
  } else {
    Resolve-TechnicalDefaults
    $privateRoot = Join-Path $trialPath 'trial-private/composed-profiles'
    New-Item -ItemType Directory -Force -Path (Join-Path $trialPath 'trial-private') | Out-Null
    $profilePath = Join-Path $privateRoot $Seat
    New-Item -ItemType Directory -Force -Path $privateRoot | Out-Null
    $overlayName = @{ 'seat-m'='formalist'; 'seat-d'='adversarial'; 'seat-g'='empirical' }[$Seat]
    & $profilePython (Join-Path $repo 'scripts/host/lib/compose_profile.py') compose `
      --technical-base (Resolve-Path $TechnicalBase).Path `
      --technical-agents (Resolve-Path $TechnicalAgents).Path `
      --technical-config (Resolve-Path $TechnicalConfig).Path `
      --overlay (Join-Path $repo "profiles/$overlayName") `
      --destination $profilePath --seat $Seat | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Technical profile composition failed.' }
  }
  & $profilePython (Join-Path $repo 'scripts/host/lib/compose_profile.py') validate $profilePath --seat $Seat | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Composed profile validation failed.' }
  & $python (Join-Path $repo 'scripts/host/lib/profile_digest.py') $profilePath | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Profile tree validation failed.' }

  if ($CredentialTarget) {
    if (-not $IsWindows) { throw '-CredentialTarget requires Windows Credential Manager.' }
    $temporarySecret = Join-Path ([IO.Path]::GetTempPath()) ("magi-provider-{0}.secret" -f [Guid]::NewGuid())
    $credential = Get-StoredCredential -Target $CredentialTarget -ErrorAction Stop
    if (-not $credential) { throw "Credential Manager target not found: $CredentialTarget" }
    [IO.File]::WriteAllText($temporarySecret, $credential.GetNetworkCredential().Password, [Text.UTF8Encoding]::new($false))
    & icacls $temporarySecret /inheritance:r /grant:r "$([Security.Principal.WindowsIdentity]::GetCurrent().Name):(R,W)" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not restrict temporary Credential Manager file ACL.' }
    $SecretFile = $temporarySecret
  }
  if (-not $SecretFile) { throw 'Provide -SecretFile or -CredentialTarget.' }
  $secretPath = (Resolve-Path $SecretFile).Path
  if (-not $IsWindows) {
    $mode = (Get-Item $secretPath).UnixFileMode
    if (($mode -band ([IO.UnixFileMode]::GroupRead -bor [IO.UnixFileMode]::GroupWrite -bor [IO.UnixFileMode]::GroupExecute -bor [IO.UnixFileMode]::OtherRead -bor [IO.UnixFileMode]::OtherWrite -bor [IO.UnixFileMode]::OtherExecute)) -ne 0) {
      throw 'Provider secret file must not grant group/other permissions.'
    }
    $env:MAGI_CONTAINER_UID = [string](& id -u)
    $env:MAGI_CONTAINER_GID = [string](& id -g)
  } else {
    # Docker Desktop runs Linux containers; host Windows SIDs are not valid container IDs.
    $env:MAGI_CONTAINER_UID = if ($env:MAGI_CONTAINER_UID) { $env:MAGI_CONTAINER_UID } else { '1000' }
    $env:MAGI_CONTAINER_GID = if ($env:MAGI_CONTAINER_GID) { $env:MAGI_CONTAINER_GID } else { '1000' }
  }

  $artifactRoot = Join-Path $trialPath 'seat-work'
  New-Item -ItemType Directory -Force -Path (Join-Path $artifactRoot $Seat) | Out-Null
  $env:MAGI_ARTIFACT_ROOT = $artifactRoot
  $env:MAGI_ORIGINAL_BRIEF = $briefPath
  $env:MAGI_EVIDENCE_ROOT = Split-Path -Parent $evidenceManifestPath
  $env:MAGI_ASSIGNMENT_PLAN = $assignmentPlanPath
  $env:MAGI_SEAT_M_PROFILE = $profilePath; $env:MAGI_SEAT_D_PROFILE = $profilePath; $env:MAGI_SEAT_G_PROFILE = $profilePath
  $env:MAGI_SEAT_M_CONFIG = $seatConfigPath; $env:MAGI_SEAT_D_CONFIG = $seatConfigPath; $env:MAGI_SEAT_G_CONFIG = $seatConfigPath
  $env:MAGI_SEAT_M_POLICY = $policyPath; $env:MAGI_SEAT_D_POLICY = $policyPath; $env:MAGI_SEAT_G_POLICY = $policyPath
  $env:MAGI_SEAT_M_SECRET_FILE = $secretPath; $env:MAGI_SEAT_D_SECRET_FILE = $secretPath; $env:MAGI_SEAT_G_SECRET_FILE = $secretPath

  & docker compose -f $compose up -d "$Seat-egress"
  if ($LASTEXITCODE -ne 0) { throw 'Seat egress sidecar failed to start.' }
  try {
    $deadline = [DateTime]::UtcNow.AddSeconds(45)
    do {
      $proxyState = (& docker compose -f $compose ps --format json "$Seat-egress" | ConvertFrom-Json).Health
      if ($proxyState -eq 'healthy') { break }
      if ($proxyState -eq 'unhealthy') { throw 'Seat egress sidecar is unhealthy.' }
      Start-Sleep -Seconds 1
    } while ([DateTime]::UtcNow -lt $deadline)
    if ($proxyState -ne 'healthy') { throw 'Seat egress sidecar did not become healthy.' }
    & docker compose -f $compose run --rm $Seat
    if ($LASTEXITCODE -ne 0) { throw "seat container failed with exit $LASTEXITCODE" }
  } finally {
    & docker compose -f $compose rm -sf "$Seat-egress" | Out-Null
  }
  $done = Join-Path $artifactRoot "$Seat/SEAT_DONE"
  if (-not (Test-Path $done)) { throw 'seat did not produce SEAT_DONE' }
  $dossier = Join-Path $artifactRoot "$Seat/dossier.json"
  if (-not (Test-Path $dossier)) { throw 'seat did not produce dossier.json' }
  if ($Json) { [Console]::Out.WriteLine((@{ seat_id = $Seat; dossier_path = $dossier } | ConvertTo-Json -Compress)) }
  else { Write-Output "dossier: $dossier" }
}
finally {
  if ($temporarySecret -and (Test-Path $temporarySecret)) { Remove-Item -Force $temporarySecret }
}

# Windows is statically/CI maintained. Real Credential Manager plus Docker Desktop
# execution is reported only after verification on a Windows host.
