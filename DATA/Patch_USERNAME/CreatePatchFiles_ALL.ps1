# ===================================================
# PowerShell скрипт для создания patch_ALL.pck файла (Windows-1251)
# Все записи в один файл, без разделения по пользователям

# ========== НАСТРОЙКИ (измените под себя) ==========
$inputFile = "F:\TO_DBI\DATA\Patch_USERNAME\3_methods2refactor.xlsx"
$outputDir = "F:\TO_DBI\DATA\Patch_USERNAME"
$sheetName = "Select methods"  # Имя листа в Excel (если не знаете, оставьте $null)
$outputFileName = "patch_ALL.pck"
# ===================================================

# Функция для получения имени листа, если не указан
function Get-SheetName {
    param($excel, $specifiedName)
    if ($specifiedName) {
        return $specifiedName
    }
    # Берём первый лист
    return $excel.Worksheets.Item(1).Name
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "СОЗДАНИЕ PATCH_ALL.PCK (Windows-1251)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка существования входного файла
if (-not (Test-Path $inputFile)) {
    Write-Host "ОШИБКА: Файл не найден: $inputFile" -ForegroundColor Red
    exit 1
}

# Создание выходного каталога
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Создан каталог: $outputDir" -ForegroundColor Green
}

Write-Host "Загрузка Excel файла..." -ForegroundColor Yellow

# Запуск Excel (COM-объект)
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    
    $workbook = $excel.Workbooks.Open($inputFile)
    $sheet = $workbook.Worksheets.Item($sheetName)
    
    Write-Host "  Лист: $($sheet.Name)" -ForegroundColor Gray
    
    # Получение используемого диапазона
    $usedRange = $sheet.UsedRange
    $rows = $usedRange.Rows.Count
    $cols = $usedRange.Columns.Count
    
    Write-Host "  Строк: $rows, Колонок: $cols" -ForegroundColor Gray
    
    # Поиск заголовков (первая строка)
    $headers = @{}
    for ($col = 1; $col -le $cols; $col++) {
        $headerValue = $sheet.Cells.Item(1, $col).Text
        if ($headerValue) {
            $headers[$headerValue] = $col
        }
    }
    
    # Проверка наличия необходимых колонок
    $requiredColumns = @("Status X", "CLASS_ID", "SHORT_NAME")
    $missingColumns = @()
    
    foreach ($col in $requiredColumns) {
        if (-not $headers.ContainsKey($col)) {
            $missingColumns += $col
        }
    }
    
    if ($missingColumns.Count -gt 0) {
        Write-Host "ОШИБКА: Не найдены колонки: $($missingColumns -join ', ')" -ForegroundColor Red
        $workbook.Close()
        $excel.Quit()
        exit 1
    }
    
    Write-Host "  Найдены колонки: $($headers.Keys -join ', ')" -ForegroundColor Gray
    
    # Сбор данных
    $data = @()
    $skippedStatus = 0
    $skippedEmpty = 0
    
    for ($row = 2; $row -le $rows; $row++) {
        $statusX = $sheet.Cells.Item($row, $headers["Status X"]).Text
        
        # Пропускаем, если Status X не пустой
        if ($statusX -ne "") {
            $skippedStatus++
            continue
        }
        
        $classId = $sheet.Cells.Item($row, $headers["CLASS_ID"]).Text
        $shortName = $sheet.Cells.Item($row, $headers["SHORT_NAME"]).Text
        
        # Пропускаем пустые строки
        if ([string]::IsNullOrWhiteSpace($classId) -or [string]::IsNullOrWhiteSpace($shortName)) {
            $skippedEmpty++
            continue
        }
        
        $data += [PSCustomObject]@{
            ClassId = $classId.Trim()
            ShortName = $shortName.Trim()
        }
    }
    
    Write-Host "  Собрано записей: $($data.Count)" -ForegroundColor Gray
    Write-Host "  Пропущено (Status X не пуст): $skippedStatus" -ForegroundColor Gray
    Write-Host "  Пропущено (пустые CLASS_ID/SHORT_NAME): $skippedEmpty" -ForegroundColor Gray
    
    # Закрываем Excel
    $workbook.Close()
    $excel.Quit()
    
    Write-Host ""
    Write-Host "Обработка данных..." -ForegroundColor Yellow
    
    # Сортировка: по ClassId, затем по ShortName
    $sortedData = $data | Sort-Object ClassId, ShortName
    
    Write-Host "  Всего записей для экспорта: $($sortedData.Count)" -ForegroundColor Gray
    
    # Формирование содержимого файла
    $content = @()
    $content += "VER2"
    $content += "REM Список элементов"
    $content += "REM CFT-Platform-IDE: 2.36.406"
    $content += ""
    
    foreach ($item in $sortedData) {
        $content += "METH $($item.ClassId) $($item.ShortName)"
    }
    
    # Запись в файл в кодировке Windows-1251
    $filepath = Join-Path $outputDir $outputFileName
    
    # Получаем кодировку Windows-1251
    $encoding = [System.Text.Encoding]::GetEncoding("windows-1251")
    
    # Запись файла
    [System.IO.File]::WriteAllLines($filepath, $content, $encoding)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "ГОТОВО!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Создан файл: $outputFileName" -ForegroundColor White
    Write-Host "  Всего записей: $($sortedData.Count)" -ForegroundColor White
    Write-Host "  Каталог: $outputDir" -ForegroundColor White
    Write-Host "  Кодировка: Windows-1251" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
    if ($excel) {
        $excel.Quit()
    }
    exit 1
}