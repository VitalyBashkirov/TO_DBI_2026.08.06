# DS_095 - Отчёт

## 1. Что сделано
- Добавлен подраздел 6.1 "Kodirovka faylov i BOM" v DS_STANDARD.md (razdel 6)
- Privedeny primery PowerShell s BOM i bez
- Ukazany sluchai DS_089a, DS_091a

## 2. Изменённые файлы
- EXCHANGE\DS_STANDARD.md - dobavlen podrazdel 6.1

## Diff DS_STANDARD.md
- Dobavlen podrazdel 6.1 "Kodirovka faylov i BOM" (okolo 45 strok)
- Razdely 1-5, 7-9 ne izmeneny

## 3. Результат тестов
- Select-String "6.1. Kodirovka" - naydena (stroka 128)
- Select-String "UTF8Encoding" - nayden
- Select-String "unexpected line" - nayden

## 4. Расхождения
- net

## 5. Артефакты
- EXCHANGE\DS_STANDARD.md (izmenen)
- EXCHANGE\OUTBOX\DS_095_report.md