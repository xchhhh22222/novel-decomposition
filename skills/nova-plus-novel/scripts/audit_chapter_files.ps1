param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath
)

$ErrorActionPreference = 'Stop'

function Join-CodePoints {
    param([int[]]$CodePoints)
    return -join ($CodePoints | ForEach-Object { [char]$_ })
}

$chapterPrefix = [string][char]0x7B2C
$chapterSuffix = [string][char]0x7AE0
$chapterFolderName = Join-CodePoints @(0x7AE0, 0x8282, 0x5185, 0x5BB9)

function Convert-ChineseChapterNumber {
    param([string]$Text)

    if ($Text -match '^\d+$') {
        return [int]$Text
    }

    $digits = @{
        0x96F6 = 0; 0x3007 = 0; 0x4E00 = 1; 0x4E8C = 2; 0x4E24 = 2
        0x4E09 = 3; 0x56DB = 4; 0x4E94 = 5; 0x516D = 6; 0x4E03 = 7
        0x516B = 8; 0x4E5D = 9
    }
    $units = @{ 0x5341 = 10; 0x767E = 100; 0x5343 = 1000 }

    $total = 0
    $section = 0
    $number = 0

    foreach ($char in $Text.ToCharArray()) {
        $code = [int]$char
        if ($digits.ContainsKey($code)) {
            $number = $digits[$code]
            continue
        }
        if ($units.ContainsKey($code)) {
            if ($number -eq 0) { $number = 1 }
            $section += $number * $units[$code]
            $number = 0
            continue
        }
        if ($code -eq 0x4E07) {
            $section += $number
            if ($section -eq 0) { $section = 1 }
            $total += $section * 10000
            $section = 0
            $number = 0
            continue
        }
        return $null
    }

    return $total + $section + $number
}

function Get-ChapterNumberFromText {
    param(
        [string]$Text,
        [bool]$AllowHeadingMarker
    )

    $candidate = $Text.Trim()
    if ($AllowHeadingMarker -and $candidate.StartsWith('#')) {
        $candidate = $candidate.Substring(1).Trim()
    }
    if (-not $candidate.StartsWith($chapterPrefix)) {
        return $null
    }

    $suffixIndex = $candidate.IndexOf($chapterSuffix, 1)
    if ($suffixIndex -lt 2) {
        return $null
    }

    $numberText = $candidate.Substring(1, $suffixIndex - 1)
    return Convert-ChineseChapterNumber $numberText
}

$resolvedProject = (Resolve-Path -LiteralPath $ProjectPath).Path
$chapterDir = Join-Path $resolvedProject $chapterFolderName
if (-not (Test-Path -LiteralPath $chapterDir -PathType Container)) {
    throw "Chapter directory not found: $chapterDir"
}

$records = foreach ($file in Get-ChildItem -LiteralPath $chapterDir -File -Filter '*.md') {
    $number = Get-ChapterNumberFromText $file.BaseName $false
    if ($null -eq $number) {
        [pscustomobject]@{
            Number = $null
            File = $file.Name
            HeadingNumber = $null
            HasHeading = $false
            Problem = 'Cannot parse chapter number from file name'
        }
        continue
    }

    $headingNumber = $null
    $hasHeading = $false
    foreach ($line in (Get-Content -LiteralPath $file.FullName -Encoding UTF8 -TotalCount 12)) {
        $parsedHeading = Get-ChapterNumberFromText $line $true
        if ($null -ne $parsedHeading) {
            $hasHeading = $true
            $headingNumber = $parsedHeading
            break
        }
    }

    $problem = $null
    if ($hasHeading -and $headingNumber -ne $number) {
        $problem = "File name is chapter $number but heading is chapter $headingNumber"
    }

    [pscustomobject]@{
        Number = $number
        File = $file.Name
        HeadingNumber = $headingNumber
        HasHeading = $hasHeading
        Problem = $problem
    }
}

$numbered = @($records | Where-Object { $null -ne $_.Number } | Sort-Object Number, File)
$duplicates = @($numbered | Group-Object Number | Where-Object Count -gt 1)
$maxNumber = if ($numbered.Count -gt 0) { ($numbered.Number | Measure-Object -Maximum).Maximum } else { 0 }
$present = @{}
foreach ($record in $numbered) { $present[$record.Number] = $true }
$missing = @()
for ($i = 1; $i -le $maxNumber; $i++) {
    if (-not $present.ContainsKey($i)) { $missing += $i }
}
$mismatches = @($records | Where-Object { $_.Problem })

Write-Output "Project: $resolvedProject"
Write-Output "Chapter files: $($records.Count); highest chapter: $maxNumber"

if ($duplicates.Count -eq 0) {
    Write-Output 'Duplicate chapter numbers: none'
} else {
    Write-Output 'Duplicate chapter numbers:'
    foreach ($group in $duplicates) {
        Write-Output "  Chapter $($group.Name)"
        foreach ($item in $group.Group) { Write-Output "    - $($item.File)" }
    }
}

if ($missing.Count -eq 0) {
    Write-Output 'Missing chapter numbers: none'
} else {
    Write-Output "Missing chapter numbers: $($missing -join ', ')"
}

if ($mismatches.Count -eq 0) {
    Write-Output 'Number mismatches: none'
} else {
    Write-Output 'Number mismatches:'
    foreach ($item in $mismatches) {
        Write-Output "  - $($item.File): $($item.Problem)"
    }
}

$withoutHeading = @($numbered | Where-Object { -not $_.HasHeading })
Write-Output "Files without a Markdown chapter heading in the first 12 lines: $($withoutHeading.Count) (informational)"

if ($duplicates.Count -gt 0 -or $mismatches.Count -gt 0) {
    Write-Output 'Result: BLOCKED. Resolve canonical chapter versions before drafting.'
} else {
    Write-Output 'Result: chapter numbering has no blockers; semantic continuity review is still required.'
}
