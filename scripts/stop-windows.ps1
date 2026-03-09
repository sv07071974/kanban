$ErrorActionPreference = "Stop"

$ContainerName = "pm-app"

$Matches = docker ps -a --format "{{.Names}}" | Select-String -SimpleMatch $ContainerName
if ($Matches) {
  docker stop $ContainerName
  docker rm $ContainerName
  Write-Host "Stopped $ContainerName."
} else {
  Write-Host "Container $ContainerName not found."
}
