# AI_RESPONSE_PSH_DEP_PRIV_GO_20260930_071636

## Метаданные
- source_file: F:\TO_DBI\PATCH_IN\patch_PSH_DEP_PRIV_GO\src\ENTITY\DEPN\PSH_DEP_PRIV_GO.plp
- request: AI_REQUEST_PSH_DEP_PRIV_GO_20260930_071636.md
- rubricator: PlpCheck
- model: 
- generated_at: 2026-10-07T03:51:09

## Фиксы

```json
[
  {
    "id": 26,
    "line": 21,
    "before": "--public METHOD2CALL\t\t[METHOD2CALL];",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 2,
    "line": 32,
    "before": "IS_EOD_NEW\t\t\tboolean;\t\t\t--признак нового ЗОДа",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 3,
    "line": 33,
    "before": "stream_num\t\t\tstring;\t\t\t\t--сконвертированный в текст номер потока",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 4,
    "line": 34,
    "before": "debug_on\t\t\tboolean;\t\t\t--признак вывода отладки в консоль",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 5,
    "line": 36,
    "before": "IdFile\t\tinteger;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 6,
    "line": 45,
    "before": "ThisClass\tvarchar2(16);",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 7,
    "line": 49,
    "before": "ComStatus_Work\t   ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'WORK');",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 8,
    "line": 50,
    "before": "ComStatus_Prol\t   ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'PROLONG');",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 9,
    "line": 51,
    "before": "ComStatus_AREST    ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'AREST');",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 10,
    "line": 52,
    "before": "ComStatus_TO_CLOSE ref [COM_STATUS_PRD] := ::[COM_STATUS_PRD]([CODE] = 'TO_CLOSE');",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 11,
    "line": 67,
    "before": "idx number := 0;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 12,
    "line": 72,
    "before": "SysOpDate\tdate;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 13,
    "line": 82,
    "before": "v_op_date\tdate;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 1,
    "line": 92,
    "before": "Function CheckHollidays(P_DATE_BEG in out date, P_DATE_END in out date, OnFilial ref [BRANCH]) return boolean is",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 27,
    "line": 118,
    "before": "--[DEPN_INTERFACE].[PRX_DEPN_TO_END].EOD2_WrMess(stream_num||TB$||to_char(sysdate, 'dd/mm/yy hh24:mi:ss')||TB$||Mess);",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 14,
    "line": 190,
    "before": "t1\tinteger;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 15,
    "line": 191,
    "before": "t2\tinteger;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 16,
    "line": 233,
    "before": "i\tnumber;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 17,
    "line": 251,
    "before": "vHours \t\t\tnumber;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 18,
    "line": 252,
    "before": "vMinutes\t\tnumber;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 19,
    "line": 253,
    "before": "vSeconds\t\tnumber;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 20,
    "line": 254,
    "before": "vMilliseconds\tnumber;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 21,
    "line": 255,
    "before": "vFraction\t\tnumber := 1000;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 34,
    "line": 274,
    "before": "/** /",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 22,
    "line": 280,
    "before": "m ref [METHOD2CALL];",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 28,
    "line": 313,
    "before": "--return ::[SYSTEM].[PSB_DAY_LIB].check_stop_commit(P_METHOD_PROC,P_OBJECT_COUNT,P_OBJECT_HANDLED,P_OBJ_HANDLE_ERROR);",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 29,
    "line": 373,
    "before": "-- End initialization of parameters and variables",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 23,
    "line": 375,
    "before": "vEnableCheckBoxes\tboolean;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 24,
    "line": 376,
    "before": "v1B400085\t\t\tboolean;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 25,
    "line": 377,
    "before": "bApp1B400302\t\t\tboolean;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 30,
    "line": 556,
    "before": "--\t::[RUNTIME].[TRACE].START_TRACE(iTLevel == 8);",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 31,
    "line": 602,
    "before": "--::[RUNTIME].[TRACE].STOP_TRACE;",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 35,
    "line": 1533,
    "before": ",P_COMISS_TYPE \t== P_COMISS_TYPES \t/*Список id видов комиссий разделенных через ;*/",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 32,
    "line": 1618,
    "before": "--rFolder := &Depn.Id->(DEPN)[ADJUSTMENT_TO_AC]( P_DATE\t\t== CurDate",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 33,
    "line": 1636,
    "before": "--- \t\t\t\t\t\t\t   sqlerrm);",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  },
  {
    "id": 36,
    "line": 2142,
    "before": "/** /",
    "after": "mock fixed line",
    "reason": "ai-local: qwen2.5-coder:7b — mock fallback test",
    "confidence": 0.95
  }
]
```
