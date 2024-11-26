param(
    [string]$file,
    [string]$string,
    [string]$style = "Requirement_ID"
)

#Write-Host "file: $file"
#Write-Host "string: $string"
#Write-Host "style: $style"

try { # try to get a running word
  $Word = [Runtime.Interopservices.Marshal]::GetActiveObject('Word.Application')
}
catch { # No word is running, start it
  $Word = New-object -comobject Word.Application
}

#Find the $file document in word
$found = $false
foreach ($doc in $Word.Documents){
  if ($doc.FullName -eq $file) { $found = $true }
}
if ( $found ) { $doc=$Word.Documents($file) }
#and open it if it is not found
else { $doc = $Word.Documents.Open($file)  }

#ensure document is active
$doc.Activate()
if (-not $string -eq "") {
  $wdstory=6 #Hard coded value representing start of document
  $Word.Selection.HomeKey($wdStory) >$null # Move selection to start of document
  $Word.Selection.Find.Text=$string # And search first $string of $style
  $Word.Selection.Find.Style=$style
  $Word.Selection.Find.Execute() >$null
}

$Word.Visible=$True # ensure document is visible
$word.Activate()
