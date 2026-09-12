# CHANGELOG — Анализ кода по рубрикатору v5.0.1

**Дата анализа**: 2026-08-18  
**Рубрикатор**: v5.0.1  
**Всего правил**: 161 (144 из v50.docx + 17 из PlpCheck)  
**Отсканировано файлов**: 599  
**Найдено проблем HIGH**: 381  

---

## Сводка проблем

| # | Правило | Кол-во | Описание |
|---|---------|--------|----------|
| 1 | v50.PROC.WHENOTHERS.п.3.5 | 369 | WHEN OTHERS без ROLLBACK/RAISE |
| 2 | v50.PROC.NATIVEID.п.3.26 | 12 | NativeID для метаданных (NUMBER вместо VARCHAR2) |
| **Итого** | | **381** | |

---

## 1. v50.PROC.WHENOTHERS.п.3.5 — WHEN OTHERS без ROLLBACK/RAISE (369 случаев)

**Приоритет**: HIGH  
**Описание**: Блок `WHEN OTHERS` должен содержать `ROLLBACK` и `RAISE` для корректной обработки ошибок.  
**Рекомендация**: Добавить `ROLLBACK; RAISE;` после `exception when others then`.

### patch_ALL

| Файл | Строка | Исходный код | Исправление |
|------|--------|-------------|-------------|
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 295 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 315 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 335 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 355 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 375 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 395 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 415 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 435 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 455 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 475 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 495 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 515 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 85 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 247 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 752 | `when others then log_err(...)` | `when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 806 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 830 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 854 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 879 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 1018 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/BASE_VAL_OP/PSH_EXP_CONTR.plp` | 187 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_CL_PRIV_INT.plp` | 260 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_CL_PRIV_INT.plp` | 393 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_CL_PRIV_INT2.plp` | 261 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_CL_PRIV_INT2.plp` | 390 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_CL_PRIV_INT4.plp` | 209 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_CL_PRIV_INT4.plp` | 348 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_ETO_A_CL_INT.plp` | 68 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_ETO_CARD_INT.plp` | 142 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_ETO_CARD_INT.plp` | 223 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_ETO_C_CT_INT.plp` | 117 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/PSH_ETO_C_DT_INT.plp` | 100 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/DOC_TAX_IN/PSH_FILE_CONTEN.plp` | 54 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/DOC_TAX_IN/PSH_PREPROCESS.plp` | 134 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/GIS_ZHKH_COND/PSH_IMPORT_INN.plp` | 120 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/IFRS_FTOOL_GRP/PSH_IMP_BUDV.plp` | 152 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/IFRS_FTOOL_GRP/PSH_IMP_BUDV.plp` | 695 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_FRX.plp` | 726 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_F_X.plp` | 77 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_F_X.plp` | 109 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_F_X.plp` | 162 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_F_X.plp` | 1538 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 86 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 135 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 1041 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 172 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 442 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 449 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 1186 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 1203 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 77 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 165 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 441 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 562 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_EVENT/PSH_LIB.plp` | 51 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LIB/PSH_GFLIB.plp` | 635 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 86 | `when OTHERS then return;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 358 | `when OTHERS then return;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 811 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 821 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 847 | `exception when OTHERS then write_log(...)` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 117 | `when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 396 | `when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 685 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 695 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 719 | `exception when OTHERS then write_log(...)` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 78 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 108 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 357 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 942 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1088 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1098 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1184 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1196 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1207 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_RFM_CTRL/PSH_RFM_DAILY.plp` | 165 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_RFM_CTRL/PSH_RFM_GLOBAL.plp` | 157 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_RFM_CTRL/PSH_RFM_JOB.plp` | 152 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_RFM_CTRL/PSH_RFM_ONCE.plp` | 165 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/REPS_DATA/PSH_LIB_DEFINE.plp` | 359 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/TAX_CL_PR_AC_INF/PSH_L.plp` | 84 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |

### patch_WORK

| Файл | Строка | Исходный код | Исправление |
|------|--------|-------------|-------------|
| `src/ENTITY/AC_FIN/PSH_LIB_2021.plp` | 220 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/AC_FIN/PSH_L_LOAN_INSP.plp` | 137 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/AC_FIN/Z1494265900.plp` | 141 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CLIENT/PSH_IMP_K.plp` | 302 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_DATE_DEATH.plp` | 64 | `exception when OTHERS then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/CL_PRIV/PSH_EDIT#AUTO_CP.plp` | 1761 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 154 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 182 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 880 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 915 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 955 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1024 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1074 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1119 | `when others then -- Выполнение операции...` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1201 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1234 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1273 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1301 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1360 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1512 | `when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1585 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1628 | `--- when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1669 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1852 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 1965 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 2026 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 2144 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/DEPN/PSH_PRN_WORD_UNI.plp` | 92 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/END_OD_OPERATION/PSH_NAST_EDIT_G5.plp` | 62 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/END_OD_OPERATION/PSH_NAST_EDIT_G5.plp` | 77 | `exception when others then nastroyka:=null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/FOLDER_PAY/PSH_TO_FORM.plp` | 83 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/MD_FOR_PROV_CP_3.plp` | 66 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/MD_FOR_PROV_CP_3.plp` | 111 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/MD_FOR_PROV_CP_3.plp` | 172 | `exception when others then debug_pipe(...)` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/MD_FOR_PROV_CP_3.plp` | 266 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 80 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 88 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 99 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 1613 | `WHEN OTHERS THEN` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 1632 | `WHEN OTHERS THEN` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 1661 | `WHEN OTHERS THEN` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 1745 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3023 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3261 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3299 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3318 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3343 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3356 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3368 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3406 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3449 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3498 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 3550 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_GETSUM_CP_2.plp` | 54 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_GETSUM_CP_2.plp` | 99 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/HOOK_BANK/RKO_GETSUM_CP_2.plp` | 134 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/IP_CARDS/PSH_WRD_V3.plp` | 194 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/IP_CARDS/PSH_WRD_V3.plp` | 207 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/IP_CARDS/PSH_WRD_V3.plp` | 232 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/MAIN_DOCUM/PSH_MAG.plp` | 122 | `exception When OTHERS Then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/MAIN_DOCUM/PSH_MAG.plp` | 208 | `exception When OTHERS Then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PR_CRED/PSH_CALC_PAR.plp` | 76 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1478 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1496 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1590 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1608 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1703 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1712 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1744 | `begin bcd.[PURPOSE_CODE] := ... exception when OTHERS then null; end;` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1844 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1885 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1895 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1929 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1954 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2184 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2338 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2348 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2460 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2593 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2740 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2842 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2852 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/TMC_DOCUM/WORK_DOCUM_SPIS.plp` | 268 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/ENTITY/TMC_DOCUM/WORK_DOCUM_SPIS.plp` | 542 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 85 | `exception when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 247 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 752 | `when others then log_err(...)` | `when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 806 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 830 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 854 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 879 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 1018 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/BASE_VAL_OP/PSH_EXP_CONTR.plp` | 187 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/DOC_TAX_IN/PSH_FILE_CONTEN.plp` | 54 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/IFRS_FTOOL_GRP/PSH_IMP_BUDV.plp` | 152 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/IFRS_FTOOL_GRP/PSH_IMP_BUDV.plp` | 695 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_FRX.plp` | 722 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 86 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 135 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 1041 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 172 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 442 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 449 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 1186 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 1203 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 77 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 165 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 441 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 562 | `when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_EVENT/PSH_LIB.plp` | 51 | `when others then null;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LIB/PSH_GFLIB.plp` | 635 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 86 | `when OTHERS then return;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 358 | `when OTHERS then return;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 811 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 821 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 847 | `exception when OTHERS then write_log(...)` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 117 | `when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 396 | `when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 685 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 695 | `exception when OTHERS then exit;` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 719 | `exception when OTHERS then write_log(...)` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 76 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 106 | `exception when OTHERS then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 355 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 934 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1080 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1090 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1176 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1188 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 1199 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/REPS_DATA/PSH_LIB_DEFINE.plp` | 359 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |
| `src/TYPE/STRUCTURE/TAX_CL_PR_AC_INF/PSH_L.plp` | 84 | `exception when others then` | `exception when others then ROLLBACK; RAISE;` |

---

## 2. v50.PROC.NATIVEID.п.3.26 — NativeID для метаданных (12 случаев)

**Приоритет**: HIGH  
**Описание**: Метаданные DBI используют VARCHAR2(38) для `%id`, а не NUMBER.  
**Рекомендация**: Заменить `NUMBER` на `VARCHAR2(38)` для переменных, используемых с `%id`.

### patch_ALL

| Файл | Строка | Исходный код | Исправление |
|------|--------|-------------|-------------|
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 217 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 245 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 273 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 301 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 329 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 357 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 385 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 413 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 441 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 469 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 497 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 525 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |

### patch_WORK

| Файл | Строка | Исходный код | Исправление |
|------|--------|-------------|-------------|
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 1960 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2179 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 2611 | `A_DocID := doc%id;` | `A_DocID varchar2(38); A_DocID := doc%id;` |

---

## Сводка изменений по файлам

| Файл | WHEN OTHERS | NativeID | Итого |
|------|-------------|----------|-------|
| `src/ENTITY/CL_PRIV/PSH_DBLINKCLIENT.plp` | 12 | 0 | 12 |
| `src/ENTITY/DEPN/PSH_DEP_PRIV_GO.plp` | 21 | 0 | 21 |
| `src/ENTITY/HOOK_BANK/RKO_CALC_PAR_333.plp` | 18 | 0 | 18 |
| `src/ENTITY/PSH_IBANK2/PSH_IBANK2.plp` | 14 | 3 | 17 |
| `src/ENTITY/PSH_IBANK2/PSH_LIB_DEP_XML.plp` | 0 | 12 | 12 |
| `src/TYPE/STRUCTURE/ASV_REESTR_FILES/PSH_EXPORT.plp` | 12 | 0 | 12 |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB.plp` | 3 | 0 | 3 |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LIB_FUN.plp` | 6 | 0 | 6 |
| `src/TYPE/STRUCTURE/PSH_CUST_DOCS/PSH_LOAD_DOCS.plp` | 6 | 0 | 6 |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB.plp` | 5 | 0 | 5 |
| `src/TYPE/STRUCTURE/PSH_LOCAL_JOB/PSH_LIB_V2.plp` | 5 | 0 | 5 |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_INIT_RECS.plp` | 3 | 0 | 3 |
| `src/TYPE/STRUCTURE/PSH_ON_OFF_SOFT/PSH_L.plp` | 6 | 0 | 6 |
| `src/TYPE/STRUCTURE/MARKET_PLACE/PSH_IMP_TRDS_F_X.plp` | 4 | 0 | 4 |
| `src/TYPE/STRUCTURE/IFRS_FTOOL_GRP/PSH_IMP_BUDV.plp` | 2 | 0 | 2 |
| `src/TYPE/STRUCTURE/CIT_INTERFACE/*.plp` | 10 | 0 | 10 |
| **Итого** | **369** | **12** | **381** |

---

## Рекомендации по внедрению

1. **WHEN OTHERS**: Добавить `ROLLBACK; RAISE;` после `exception when others then`
2. **NativeID**: Заменить `NUMBER` на `VARCHAR2(38)` для переменных с `%id`
3. **Тестирование**: После исправлений протестировать обработку ошибок и метаданные

---

*CHANGELOG сгенерирован автоматически на основе анализа рубрикатора v5.0.1* — Адаптация АРМ-модулей под DBI (PostgreSQL)

## Дата: 2026-08-17 20:56:31
## Рубрикатор: v5.0.0 (160 правил)
## Версия итерации: 20260817_205606

---

### Параметры обработки

| Параметр | Значение |
|----------|----------|
| Источник | `PATCH_IN` |
| Результат | `PATCH_OUT` |
| Правила | v50, тдс20240828, тклоик20240828 |
| PlpCheck | Выключен |
| Рекурсивный поиск | Да |
| Сохранять структуру | Да |
| Только модифицированные | Да |

---

### Сводка результатов

| Метрика | Значение |
|---------|----------|
| Файлов просканировано | 598 |
| Проблем найдено | 16269 |
| Файлов создано/исправлено | 227 |

---

### Категории правил рубрикатора v5.0.0

| Категория | Количество правил | Описание |
|-----------|-------------------|----------|
| SQL/DML | 36 | Преобразование SQL-синтаксиса Oracle → ANSI SQL |
| Хранение (STOR) | 16 | Типы данных, индексы, секционирование |
| Процедурный код (PROC) | 48 | PL/SQL → PLPlus процедуры |
| Интеграции (INT) | 5 | Замена Oracle-пакетов на DBI-аналоги |
| Кэширование (CACHE) | 14 | Настройка кэша Hibernate |
| Разработка (DEV) | 17 | Ограничения разработки |
| Локальные объекты (LOCAL) | 8 | Локальные объекты DBI |
| PlpCheck (STYLE) | 16 | Стиль кода (опционально) |
| **Итого** | **160** | |

---

### Применённые автоматические исправления

Следующие правила были применены автоматически (regex-преобразования из `5.RUBRICATOR_PARSER_SQL v5.json`):

- `v50.SQL.OUTERJOIN.п.1.1` — Замена `(+)` на `LEFT/RIGHT JOIN`
- `v50.SQL.ROWNUM.п.1.2` — Замена `ROWNUM` на `FETCH FIRST`
- `v50.SQL.DECODE.п.1.6.1` — Замена `DECODE` на `CASE`
- `v50.SQL.HINTS.п.1.18` — Удаление подсказок оптимизатора
- `v50.STOR.DATE.п.2.2` — Замена `DATE` на `DATE_TIME`
- `v50.PROC.WHENOTHERS.п.3.5` — Добавление `ROLLBACK`/`RAISE` в `WHEN OTHERS`
- `v50.PROC.EXECUTE.п.3.3` — Экранирование имён таблиц в `EXECUTE IMMEDIATE`
- `v50.PROC.MACROS.п.3.4` — Удаление макросов `execute`/`process`

### Правила, требующие ручного исправления (hybrid)

Следующие правила помечены в коде комментариями `--NEW` для ручного исправления:

- `v50.SQL.CONNECTBY.п.1.8` — Преобразование `CONNECT BY` в `WITH RECURSIVE`
- `v50.SQL.DECODE.п.1.6.1` (complex) — Сложный `DECODE` → `CASE WHEN`
- `v50.PROC.WHENOTHERS.п.3.5` (multiline) — Многострочный `WHEN OTHERS`
- И другие hybrid-правила (см. `5.RUBRICATOR_PARSER_SQL v5.json`)

---

### Структура результата

```
PATCH_OUT/
├── patch_RV/          # Результаты для patch_RV
│   └── src/ENTITY/...
├── patch_WORK/        # Результаты для patch_WORK
│   └── src/ENTITY/...
├── patch_ALL/         # Результаты для patch_ALL
├── patch_TEST_DS/     # Результаты для patch_TEST_DS
└── ...
```

---

### Следующие шаги

1. Проверить файлы в `PATCH_OUT` на корректность
2. Исправить hybrid-правила вручную (по комментариям `--NEW`)
3. Запустить повторное сканирование для проверки
4. При необходимости включить PlpCheck-правила (флаг `--plpcheck`)

---

*Сгенерировано автоматически 2026-08-17 20:56:31*
