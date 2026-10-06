# AI_RESPONSE_PSH_DEP_PRIV_GO_20260930_071636

## Метаданные
- source_file: F:\TO_DBI\PATCH_IN\patch_PSH_DEP_PRIV_GO\src\ENTITY\DEPN\PSH_DEP_PRIV_GO.plp
- request: AI_REQUEST_PSH_DEP_PRIV_GO_20260930_071636.md
- rubricator: PlpCheck
- model: 
- generated_at: 2026-10-07T02:33:56

## Фиксы

```json
[
  {
    "id": 26,
    "line": 21,
    "before": "--public METHOD2CALL\t\t[METHOD2CALL];",
    "after": "--METHOD2CALL [METHOD2CALL];",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 1.0
  },
  {
    "id": 2,
    "line": 32,
    "before": "IS_EOD_NEW\t\t\tboolean;\t\t\t--признак нового ЗОДа",
    "after": "v_bIS_EOD_NEW boolean;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 3,
    "line": 33,
    "before": "stream_num\t\t\tstring;\t\t\t\t--сконвертированный в текст номер потока",
    "after": "string v_sStream_num;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 4,
    "line": 34,
    "before": "debug_on\t\t\tboolean;\t\t\t--признак вывода отладки в консоль",
    "after": "v_bDebug_on boolean;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 5,
    "line": 36,
    "before": "IdFile\t\tinteger;",
    "after": "v_iIdFile integer;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 6,
    "line": 45,
    "before": "ThisClass\tvarchar2(16);",
    "after": "ThisClass varchar2(16);",
    "reason": "ai-local: qwen2.5-coder:7b — Не корректный префикс, пожалуйста переименуйте в \"v_sThisClass\"",
    "confidence": 0.95
  },
  {
    "id": 7,
    "line": 49,
    "before": "ComStatus_Work\t   ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'WORK');",
    "after": "v_rComStatus_Work ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'WORK');",
    "reason": "ai-local: qwen2.5-coder:7b — Не корректный префикс, пожалуйста переименуйте в \"v_rComStatus_Work\"",
    "confidence": 0.95
  },
  {
    "id": 8,
    "line": 50,
    "before": "ComStatus_Prol\t   ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'PROLONG');",
    "after": "v_rComStatus_Prol",
    "reason": "ai-local: qwen2.5-coder:7b — Не корректный префикс, пожалуйста переименуйте в \"v_rComStatus_Prol\"",
    "confidence": 0.95
  },
  {
    "id": 9,
    "line": 51,
    "before": "ComStatus_AREST    ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'AREST');",
    "after": "v_rComStatus_AREST ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'AREST');",
    "reason": "ai-local: qwen2.5-coder:7b — Не корректный префикс, пожалуйста переименуйте в \"v_rComStatus_AREST\"",
    "confidence": 0.95
  },
  {
    "id": 10,
    "line": 52,
    "before": "ComStatus_TO_CLOSE ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'TO_CLOSE');",
    "after": "ComStatus_TO_CLOSE ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'TO_CLOSE');",
    "reason": "ai-local: qwen2.5-coder:7b — Не корректный префикс, пожалуйста переименуйте в \"v_rComStatus_TO_CLOSE\"",
    "confidence": 0.95
  },
  {
    "id": 11,
    "line": 67,
    "before": "idx number := 0;",
    "after": "v_nIdx number := 0;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 12,
    "line": 72,
    "before": "SysOpDate\tdate;",
    "after": "v_dSysOpDate date;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 13,
    "line": 82,
    "before": "v_op_date\tdate;",
    "after": "v_dV_op_date date;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 1,
    "line": 92,
    "before": "Function CheckHollidays(P_DATE_BEG in out date, P_DATE_END in out date, OnFilial ref [BRANCH]) return boolean is",
    "after": "Function CheckHollidays(p_date_beg in out date, p_date_end in out date, onFilial ref [BRANCH]) return boolean is",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 27,
    "line": 118,
    "before": "--[DEPN_INTERFACE].[PRX_DEPN_TO_END].EOD2_WrMess(stream_num||TB$||to_char(sysdate, 'dd/mm/yy hh24:mi:ss')||TB$||Mess);",
    "after": "--[DEPN_INTERFACE].[PRX_DEPN_TO_END].EOD2_WrMess(stream_num||TB$||to_char(sysdate, 'dd/mm/yy hh24:mi:ss')||TB$||Mess);",
    "reason": "ai-local: qwen2.5-coder:7b — Удалите закомментированный код",
    "confidence": 0.95
  },
  {
    "id": 14,
    "line": 190,
    "before": "t1\tinteger;",
    "after": "v_iT1 integer;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 15,
    "line": 191,
    "before": "t2\tinteger;",
    "after": "v_iT2 integer;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 16,
    "line": 233,
    "before": "i\tnumber;",
    "after": "v_nI number;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 17,
    "line": 251,
    "before": "vHours \t\t\tnumber;",
    "after": "v_nHours number;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 18,
    "line": 252,
    "before": "vMinutes\t\tnumber;",
    "after": "v_nMinutes number;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 19,
    "line": 253,
    "before": "vSeconds\t\tnumber;",
    "after": "v_nSeconds number;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 20,
    "line": 254,
    "before": "vMilliseconds\tnumber;",
    "after": "v_nMilliseconds number;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 21,
    "line": 255,
    "before": "vFraction\t\tnumber := 1000;",
    "after": "v_nFraction number := 1000;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 34,
    "line": 274,
    "before": "/** /",
    "after": "",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 1.0
  },
  {
    "id": 22,
    "line": 280,
    "before": "m ref [METHOD2CALL];",
    "after": "m ref [v_rM];",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 28,
    "line": 313,
    "before": "--return ::[SYSTEM].[PSB_DAY_LIB].check_stop_commit(P_METHOD_PROC,P_OBJECT_COUNT,P_OBJECT_HANDLED,P_OBJ_HANDLE_ERROR);",
    "after": "--return ::[SYSTEM].[PSB_DAY_LIB].check_stop_commit(P_METHOD_PROC,P_OBJECT_COUNT,P_OBJECT_HANDLED,P_OBJ_HANDLE_ERROR);",
    "reason": "ai-local: qwen2.5-coder:7b — Удалите закомментированный код",
    "confidence": 0.95
  },
  {
    "id": 29,
    "line": 373,
    "before": "-- End initialization of parameters and variables",
    "after": "-- End initialization of parameters and variables",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 1.0
  },
  {
    "id": 23,
    "line": 375,
    "before": "vEnableCheckBoxes\tboolean;",
    "after": "v_bEnableCheckBoxes boolean;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 24,
    "line": 376,
    "before": "v1B400085\t\t\tboolean;",
    "after": "v_bV1B400085 boolean;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 25,
    "line": 377,
    "before": "bApp1B400302\t\t\tboolean;",
    "after": "v_bApp1B400302 boolean;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 30,
    "line": 556,
    "before": "--\t::[RUNTIME].[TRACE].START_TRACE(iTLevel == 8);",
    "after": "-- TRACE.START_TRACE(iTLevel == 8);",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 31,
    "line": 602,
    "before": "--::[RUNTIME].[TRACE].STOP_TRACE;",
    "after": "--::[RUNTIME].[TRACE].STOP_TRACE;",
    "reason": "ai-local: qwen2.5-coder:7b — Удалите закомментированный код",
    "confidence": 0.95
  },
  {
    "id": 35,
    "line": 1533,
    "before": ",P_COMISS_TYPE \t== P_COMISS_TYPES \t/*Список id видов комиссий разделенных через ;*/",
    "after": ",P_COMISS_TYPE  /*Список id видов комиссий разделенных через ;*/",
    "reason": "ai-local: qwen2.5-coder:7b — Удалите закомментированный код",
    "confidence": 0.95
  },
  {
    "id": 32,
    "line": 1618,
    "before": "--rFolder := &Depn.Id->(DEPN)[ADJUSTMENT_TO_AC]( P_DATE\t\t== CurDate",
    "after": "--rFolder := &Depn.Id->(DEPN)[ADJUSTMENT_TO_AC]( P_DATE == CurDate,",
    "reason": "ai-local: qwen2.5-coder:7b — Удалите закомментированный код",
    "confidence": 0.95
  },
  {
    "id": 33,
    "line": 1636,
    "before": "--- \t\t\t\t\t\t\t   sqlerrm);",
    "after": "-- sqlerrm;",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 0.95
  },
  {
    "id": 36,
    "line": 2142,
    "before": "/** /",
    "after": "",
    "reason": "ai-local: qwen2.5-coder:7b",
    "confidence": 1.0
  }
]
```
