# copy the files *.srg to %APPDATA%/SCADE/Customize and
# replace %TARGETDIR%[^/]* by the current directory
$files = (Get-ChildItem -Path . -Filter *r?.srg)
foreach ($file in $files) {
    $text = (Get-Content $file)
    $curdir = $file.Directory -replace "\\", "/"
    $textmodified = $text -replace '%TARGETDIR%[^/]*', $curdir
    $newfile = $env:APPDATA + "\SCADE\Customize\$file"
    $newfile = [System.IO.FileInfo]$newfile
    if ($newfile.Exists) {
        $bakfile = $newfile.FullName + ".bak"
        Move-Item $newfile.FullName $bakfile
    }
    Write-Host $file.Name copied to $newfile.FullName
    $textmodified | Set-Content -Path $newfile
}
