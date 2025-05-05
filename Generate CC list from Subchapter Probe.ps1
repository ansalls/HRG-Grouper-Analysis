# Go to your project root
Set-Location -Path 'C:\Users\TonyS\OneDrive\Desktop\Code\reimboost'

# Variables that are run specific
$FileName    = 'CC_Probe_FF_v2_output_2025-04-28_123743_FCE_v2_v2_v2.csv'
$Chapter   = 'FF'

# Define base directories & files 
$BaseDir = (Get-Location).Path
$HRGInputDir   = Join-Path $BaseDir 'data\hrg_input'
$HRGOutputDir  = Join-Path $BaseDir 'data\hrg_output'
$RdfFile       = Join-Path $BaseDir 'data\Max_OPCS_and_ICD10_Extended.rdf'

# Common vars
$Extension = 'csv'
$Step      = 1

# Initial input file
$StartFolder = Join-Path $BaseDir 'data\hrg_output\mini\'
$InputFile   = Join-Path $StartFolder $FileName

# Helper to build "chapter_step.ext" filenames
function Get-OutputFile {
    param(
        [int]$Step,
        [string]$Dir
    )
    return Join-Path $Dir ("{0}_{1}.{2}" -f $Chapter, $Step, $Extension)
}
# Helper to track step processing time. 
function Log-Step {
    param(
        [int] $Step,
        [System.Diagnostics.Stopwatch] $Timer
    )
    $Timer.Stop()
    Write-Host "Step $Step took $($Timer.Elapsed)"
    $Timer.Restart()
}

$timer = [System.Diagnostics.Stopwatch]::StartNew()
# Step 1: Drop rows if column doesnt (-n) contain a value (col 230, val 1)
$OutputFile = Get-OutputFile -Step $Step -Dir $StartFolder
& (Join-Path $BaseDir 'drop_if_col_contains.exe') -n $InputFile $OutputFile 230 1
Log-Step -Step $Step -Timer $timer

# Prep for next step
$InputFile = $OutputFile
$Step++

# Step 2: Drop rows where keys overlap
$OutputFile = Get-OutputFile -Step $Step -Dir $StartFolder
& (Join-Path $BaseDir 'drop_if_key_overlap.exe') $InputFile $OutputFile
Log-Step -Step $Step -Timer $timer

$InputFile = $OutputFile
$Step++

# Step 3: Append diagnoses for CC inclusion
$OutputFile = Get-OutputFile -Step $Step -Dir $StartFolder
& (Join-Path $BaseDir 'append_diag.exe') (Join-Path $BaseDir 'data\all_used_diag_codes.txt') $InputFile $OutputFile
Log-Step -Step $Step -Timer $timer

$InputFile = $OutputFile
$Step++

# Step 4: Move into the HRG input folder for the grouper
$LeafName   = Split-Path $InputFile -Leaf
$MovedPath  = Join-Path $HRGInputDir $LeafName
Move-Item -Path $InputFile -Destination $MovedPath

$InputFile = $MovedPath
$Step++

# Step 5: Run the HRG grouper
$OutputFile = Join-Path $HRGOutputDir ("{0}_{1}.{2}" -f $Chapter, $Step, $Extension)
& 'C:\Program Files\NHS England\HRG4+ 2024_25 Payment Grouper\HRGGrouperc.exe' `
    -i $InputFile `
    -o $OutputFile `
    -d $RdfFile `
    -l 'APC' `
    -h
Log-Step -Step $Step -Timer $timer

# Grouper appends "_FCE" before the extension:
$InputFile = Join-Path $HRGOutputDir ("{0}_{1}_FCE.{2}" -f $Chapter, $Step, $Extension)
$Step++
$OutputFile = Get-OutputFile -Step $Step -Dir $HRGOutputDir

# Step 6: Drop if HRG didn't change at all (cols 226 vs 291)
& (Join-Path $BaseDir 'col_substring_compare.exe') -n $InputFile $OutputFile 226 291
Log-Step -Step $Step -Timer $timer

$InputFile = $OutputFile
$Step++
$OutputFile = Get-OutputFile -Step $Step -Dir $HRGOutputDir

# Step 7: Drop if HRG root itself changed (compare first 4 chars)
& (Join-Path $BaseDir 'col_substring_compare.exe') -l 4 $InputFile $OutputFile 226 291
Log-Step -Step $Step -Timer $timer

$InputFile = $OutputFile
$Step++
$OutputFile = Get-OutputFile -Step $Step -Dir $HRGOutputDir

# Step 8: Split the appended diagnosis code from PROVSPNO field off into its own column
#    (-n -1 means split off the last delimited field)
& (Join-Path $BaseDir 'split_field.exe') -n -1 $InputFile $OutputFile 2
Log-Step -Step $Step -Timer $timer

$InputFile = $OutputFile
$Step++

# Step 9: Extract unique CC codes from the final file
$FinalDir   = Join-Path $BaseDir 'data\cc_codes'
$OutputFile = Join-Path $FinalDir ("{0}_{1}_cc_list.{2}" -f $Chapter, $Step, $Extension)
& (Join-Path $BaseDir 'unique_col_vals.exe') -c $InputFile $OutputFile 3
Log-Step -Step $Step -Timer $timer

Write-Host "Final CC list for chapter $Chapter is at $OutputFile"
