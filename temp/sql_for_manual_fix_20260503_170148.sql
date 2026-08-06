-- ФАЙЛ: SQL конструкции для ручного исправления
-- Дата генерации: 2026-05-03 17:01:48
-- Всего проблем: 35
-- Файлов: 2

-- ВАЖНО: Этот файл содержит список всех найденных проблемных конструкций.
-- Используйте его для ручного исправления или анализа.

================================================================================

--==============================================================================
-- ФАЙЛ: F:\TO_DBI\PATCH_IN\patch_RV\src\ENTITY\AC_FIN\PSH_311P_CHK.plp
-- Проблем: 5
--==============================================================================

-- Строка 14: 2 проблем(ы)
-- >>> procedure Draw(P_DATE_START	date, P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date
--   Проблема 2: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 74: 2 проблем(ы)
-- >>> 						 	ac%id = gj.[ACCOUNT](true)
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)
--   Проблема 2: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Конструкция like ac%id = gj.[ACCOUNT](true)
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 75: 1 проблем(ы)
-- >>> 				 		and gj.[IN_FILE_HISTORY] = st.collection_id(true)
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку (без квадратных скобок) с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


--==============================================================================
-- ФАЙЛ: F:\TO_DBI\PATCH_IN\patch_RV\src\ENTITY\RES_BASE_ACCS\PSH_REP_PROV_XL.plp
-- Проблем: 30
--==============================================================================

-- Строка 18: 1 проблем(ы)
-- >>> 	 ,P_DATE 	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 43: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 67: 1 проблем(ы)
-- >>> 	 ,P_DATE  date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 147: 1 проблем(ы)
-- >>> 	,P_DATE		date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 150: 1 проблем(ы)
-- >>> p_date_prev		date;
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 195: 1 проблем(ы)
-- >>> 	 ,P_DATE 	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 210: 1 проблем(ы)
-- >>> 		       where ((z.[DATE_BEGIN] <= P_DATE and not p_prev) or (z.[DATE_BEGIN] < P_DATE and p_prev))
--   Проблема 1: v50.SQL.UDF.п.1.3
--   Описание: UDF в WHERE
--   Пример исправления: order by my_func(name)


-- Строка 220: 1 проблем(ы)
-- >>> 		       where ((z.[DATE_BEGIN] <= P_DATE and not p_prev) or (z.[DATE_BEGIN] < P_DATE and p_prev))
--   Проблема 1: v50.SQL.UDF.п.1.3
--   Описание: UDF в WHERE
--   Пример исправления: order by my_func(name)


-- Строка 234: 1 проблем(ы)
-- >>> 		       where ((z.[DATE_BEGIN] <= P_DATE and not p_prev) or (z.[DATE_BEGIN] < P_DATE and p_prev))
--   Проблема 1: v50.SQL.UDF.п.1.3
--   Описание: UDF в WHERE
--   Пример исправления: order by my_func(name)


-- Строка 249: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 270: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 287: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 308: 1 проблем(ы)
-- >>> 	 ,P_DATE 	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 412: 1 проблем(ы)
-- >>>      out_debt_date 	 date;
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 486: 1 проблем(ы)
-- >>> 	date_first		date;
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 542: 1 проблем(ы)
-- >>> 					P_DATE	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 903: 1 проблем(ы)
-- >>> procedure calc_kred(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 948: 1 проблем(ы)
-- >>> 			and res.[ACC](true) = ac
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 989: 1 проблем(ы)
-- >>> procedure calc_gar(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 1034: 2 проблем(ы)
-- >>> 			and (res.[ACC](true) = ac or res.[PROD_RES](true) = port)
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)
--   Проблема 2: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1036: 1 проблем(ы)
-- >>> 			and port.[ACCRS](true) = port_acc%collection
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1037: 1 проблем(ы)
-- >>> 			and port_acc.[RES_ACC](true) = ac
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1038: 1 проблем(ы)
-- >>> 			and port_acc.[DATE_BEGIN](true) <= P_DATE
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1039: 2 проблем(ы)
-- >>> 			and (port_acc.[DATE_END](true) is null or port_acc.[DATE_END](true) > P_DATE)
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)
--   Проблема 2: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1075: 1 проблем(ы)
-- >>> procedure calc_mbk(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 1119: 1 проблем(ы)
-- >>> 			and res.[ACC](true) = ac
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1159: 1 проблем(ы)
-- >>> procedure calc_POT(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 1203: 1 проблем(ы)
-- >>> procedure calc_other(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date

