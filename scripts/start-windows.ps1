$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $RootDir "..")

$ImageName = "pm-app"
$ContainerName = "pm-app"

docker build -t $ImageName .

$Matches = docker ps -a --format "{{.Names}}" | Select-String -SimpleMatch $ContainerName
if ($Matches) {
	docker rm -f $ContainerName
}

docker run -d --name $ContainerName -p 8000:8000 --env-file .env $ImageName

Write-Host "Running at http://127.0.0.1:8000"
