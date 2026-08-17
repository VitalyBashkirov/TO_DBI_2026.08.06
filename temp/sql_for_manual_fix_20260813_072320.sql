-- ФАЙЛ: SQL конструкции для ручного исправления
-- Дата генерации: 2026-08-13 07:23:20
-- Всего проблем: 203
-- Файлов: 2

-- ВАЖНО: Этот файл содержит список всех найденных проблемных конструкций.
-- Используйте его для ручного исправления или анализа.

================================================================================

--==============================================================================
-- ФАЙЛ: F:\TO_DBI\PATCH_IN\patch_RV\src\ENTITY\AC_FIN\PSH_311P_CHK.plp
-- Проблем: 17
--==============================================================================

-- Строка 12: 1 проблем(ы)
-- >>> type prev_opened_acc_tbl is table of prev_opened_acc_type index by varchar2(16);
--   Проблема 1: v50.PROC.ID_SIZE.п.3.27
--   Описание: Объявление VARCHAR2/STRING переменной


-- Строка 14: 2 проблем(ы)
-- >>> procedure Draw(P_DATE_START	date, P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date
--   Проблема 2: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 23: 1 проблем(ы)
-- >>> 	s_idx				varchar2(16);
--   Проблема 1: v50.PROC.ID_SIZE.п.3.27
--   Описание: Объявление VARCHAR2/STRING переменной


-- Строка 56: 1 проблем(ы)
-- >>> 								and (   coalesce(gj.[FILENAME],'SBC0') like 'SBC0%' or coalesce(gj.[FILENAME],'SBC1') like 'SBC1%'	 -- Юрики
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 57: 1 проблем(ы)
-- >>> 									 or coalesce(gj.[FILENAME],'SFC0') like 'SFC0%' or coalesce(gj.[FILENAME],'SFC1') like 'SFC1%') -- Физики
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 61: 1 проблем(ы)
-- >>> 								 and (coalesce(gj.[FILENAME],'SBC2') like 'SBC2%' or coalesce(gj.[FILENAME],'SFC2') like 'SFC2%')
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 71: 1 проблем(ы)
-- >>> 						where st.[SOC_FUND] is null and st.[IN_FILE_DATETIME] <  (P_DATE + 1)
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 74: 1 проблем(ы)
-- >>> 						 	ac%id = gj.[ACCOUNT](true)
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 75: 1 проблем(ы)
-- >>> 				 		and gj.[IN_FILE_HISTORY] = st.collection_id(true)
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку (без квадратных скобок) с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 181: 1 проблем(ы)
-- >>> 				&xl.put(RowOffset + row_idx(sh), ColOffset + 1 , ac.main_v_id);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 182: 1 проблем(ы)
-- >>> 				&xl.put(RowOffset + row_idx(sh), ColOffset + 2 , ac.ClientName);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 183: 1 проблем(ы)
-- >>> 				&xl.put(RowOffset + row_idx(sh), ColOffset + 3 , to_char(case when CloseOpen = '1' then ac.OpDate else ac.ClDate end, 'dd/mm/yyyy'));
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 184: 1 проблем(ы)
-- >>> 				&xl.put(RowOffset + row_idx(sh), ColOffset + 4 , to_char(ac.WrkDate, 'dd/mm/yyyy'));
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 185: 1 проблем(ы)
-- >>> 				&xl.put(RowOffset + row_idx(sh), ColOffset + 5 , to_char(ac.AnswDate, 'dd/mm/yyyy'));
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 186: 1 проблем(ы)
-- >>> 				&xl.put(RowOffset + row_idx(sh), ColOffset + 6 , case when 	ac.RESULT='F' then 'Принят НО'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 192: 1 проблем(ы)
-- >>> 					&xl.put(RowOffset + row_idx(sh), ColOffset + 7 , case when CloseOpen=1 then 'Открыт' when CloseOpen=0 then 'Закрыт' else 'Null' end  );
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


--==============================================================================
-- ФАЙЛ: F:\TO_DBI\PATCH_IN\patch_RV\src\ENTITY\RES_BASE_ACCS\PSH_REP_PROV_XL.plp
-- Проблем: 186
--==============================================================================

-- Строка 17: 1 проблем(ы)
-- >>> 	  P_PROD 	ref [PRODUCT]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 18: 1 проблем(ы)
-- >>> 	 ,P_DATE 	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 21: 1 проблем(ы)
-- >>> ) return ref [ZALOG] is
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 31: 1 проблем(ы)
-- >>> 			  and F.A('В' || zz.[ACC_ZALOG].[ARC_MOVE] || 'сН', P_DATE + 1) <> 0
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 42: 1 проблем(ы)
-- >>> 	 P_PROD ref [PRODUCT]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 43: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 51: 1 проблем(ы)
-- >>> 		select x(sum(F.A('В' || x.[ACC_ZALOG].[ARC_MOVE] || 'сН', P_DATE + 1) * x.[VID_GUARANTEE].[SECS_CALCS_PARTS].[FACTOR]) :ob_sum)
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 55: 1 проблем(ы)
-- >>> 			  and F.A('В' || x.[ACC_ZALOG].[ARC_MOVE] || 'сН', P_DATE + 1) <> 0
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 64: 1 проблем(ы)
-- >>> 	  P_PROD  ref [PRODUCT]		  default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 65: 1 проблем(ы)
-- >>> 	 ,P_HOA	  ref [HOZ_OP_ACC]	  default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 66: 1 проблем(ы)
-- >>> 	 ,P_RES	  ref [RES_BASE_ACCS] default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 67: 1 проблем(ы)
-- >>> 	 ,P_DATE  date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 70: 1 проблем(ы)
-- >>> 	v_cat		number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 71: 1 проблем(ы)
-- >>> 	v_cat_prc	number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 72: 1 проблем(ы)
-- >>> 	v_coll		number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 144: 1 проблем(ы)
-- >>> 	 P_PROD		ref [PRODUCT]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 145: 1 проблем(ы)
-- >>> 	,P_ACC		ref [AC_FIN]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 146: 1 проблем(ы)
-- >>> 	,P_RES		ref [RES_BASE_ACCS] default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


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


-- Строка 192: 1 проблем(ы)
-- >>> 	  P_PROD	ref [PRODUCT]		default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 193: 1 проблем(ы)
-- >>> 	 ,P_HOA		ref [HOZ_OP_ACC]	default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 194: 1 проблем(ы)
-- >>> 	 ,P_RES		ref [RES_BASE_ACCS] default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 195: 1 проблем(ы)
-- >>> 	 ,P_DATE 	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 198: 1 проблем(ы)
-- >>> 	 ,P_PORT	ref [RES_PORT] default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 200: 1 проблем(ы)
-- >>> 	v_hoa_type		ref [TIP_ACC];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


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


-- Строка 248: 1 проблем(ы)
-- >>> 	 P_ACC ref [AC_FIN]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 249: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 269: 1 проблем(ы)
-- >>> 	 P_PORT ref [RES_PORT]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 270: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 272: 1 проблем(ы)
-- >>> v_summ number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 274: 1 проблем(ы)
-- >>> 	select p(sum(F.A('В' || p.[RES_ACC].[ARC_MOVE] || 'СН', P_DATE + 1)))
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 286: 1 проблем(ы)
-- >>> 	 P_PORT ref [RES_PORT]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 287: 1 проблем(ы)
-- >>> 	,P_DATE date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 289: 1 проблем(ы)
-- >>> v_summ number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 291: 1 проблем(ы)
-- >>> 	select p(sum(F.A('В' || p.[RES_ACC].[ARC_MOVE] || 'СН', P_DATE + 1) * get_prc_ifrs_on_acc(p.[RES_ACC], P_DATE))
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 305: 1 проблем(ы)
-- >>> 	  P_PROD	ref [PRODUCT]		default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 306: 1 проблем(ы)
-- >>> 	 ,P_HOA		ref [HOZ_OP_ACC]	default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 307: 1 проблем(ы)
-- >>> 	 ,P_RES		ref [RES_BASE_ACCS] default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 308: 1 проблем(ы)
-- >>> 	 ,P_DATE 	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 310: 1 проблем(ы)
-- >>> ) return ref [AC_FIN] is
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 311: 1 проблем(ы)
-- >>> 	v_hoa_type		ref [TIP_ACC];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 312: 1 проблем(ы)
-- >>> 	v_hoa_type_s	ref [TIP_ACC];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 357: 1 проблем(ы)
-- >>> 		       	 		(P_RES.[ACC].[MAIN_V_ID] like '47443%' and ac.[ACCOUNT_DOG].[1].[2].[MAIN_V_ID] like '47441%')
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 359: 1 проблем(ы)
-- >>> 		       	 		(P_RES.[ACC].[MAIN_V_ID] like '47502%' and ac.[ACCOUNT_DOG].[1].[2].[MAIN_V_ID] like '47501%')
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 366: 1 проблем(ы)
-- >>> 	elsif p_rekv = 'UNREC' and P_HOA.[ACCOUNT_DOG].[1].[2].[MAIN_V_ID] like '47440%' then
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 370: 1 проблем(ы)
-- >>> 		       	 and  ac.[ACCOUNT_DOG].[1].[2].[MAIN_V_ID] like '47442%'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 408: 1 проблем(ы)
-- >>>                   ,in_acc in ref [AC_FIN]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 412: 1 проблем(ы)
-- >>>      out_debt_date 	 date;
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 427: 1 проблем(ы)
-- >>> 		        order by nvl(x.[STAMP], x.[DATE]) desc, x%id desc
--   Проблема 1: v50.SQL.UDF.п.1.3
--   Описание: UDF в ORDER BY
--   Пример исправления: order by my_func(name)


-- Строка 456: 1 проблем(ы)
-- >>> 	            order by nvl(x.[STAMP], x.[DATE]) desc, x%id desc
--   Проблема 1: v50.SQL.UDF.п.1.3
--   Описание: UDF в ORDER BY
--   Пример исправления: order by my_func(name)


-- Строка 482: 1 проблем(ы)
-- >>>                   ,in_acc in ref [AC_FIN]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 485: 1 проблем(ы)
-- >>> 	ac_prev			ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 486: 1 проблем(ы)
-- >>> 	date_first		date;
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 504: 1 проблем(ы)
-- >>> 	&debug('(in_date_op - date_first + 1) =' || -(in_date_op - date_first + 1), 0)
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 505: 1 проблем(ы)
-- >>> 	if -(in_date_op - date_first + 1) = P_DEBT_PERIOD then 	-- Проверяем, что входящий счет не обнулялся
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 513: 1 проблем(ы)
-- >>> 				  and g.[ACCOUNT_DOG].[1].[2].[MAIN_V_ID] like '458%'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 542: 1 проблем(ы)
-- >>> 					P_DATE	date
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 543: 1 проблем(ы)
-- >>> 					,P_ACC	ref [AC_FIN]
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 544: 1 проблем(ы)
-- >>> 					,P_PROD	ref [PRODUCT]	    default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 545: 1 проблем(ы)
-- >>> 					,P_HOA	ref [HOZ_OP_ACC]	default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 546: 1 проблем(ы)
-- >>> 					,P_RES	ref [RES_BASE_ACCS] default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 547: 1 проблем(ы)
-- >>> 					,P_PORT ref [RES_PORT]		default null
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 553: 1 проблем(ы)
-- >>> 	v_cat		varchar2(3);
--   Проблема 1: v50.PROC.ID_SIZE.п.3.27
--   Описание: Объявление VARCHAR2/STRING переменной


-- Строка 554: 1 проблем(ы)
-- >>> 	v_cat_prc	number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 555: 1 проблем(ы)
-- >>> 	v_cat_prc_err varchar2(30);
--   Проблема 1: v50.PROC.ID_SIZE.п.3.27
--   Описание: Объявление VARCHAR2/STRING переменной


-- Строка 557: 1 проблем(ы)
-- >>> 	v_acc_priz	ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 561: 1 проблем(ы)
-- >>> 	v_r_res		number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 562: 1 проблем(ы)
-- >>> 	v_zalog_1	ref [ZALOG];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 563: 1 проблем(ы)
-- >>> 	v_zalog_2	ref [ZALOG];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 565: 1 проблем(ы)
-- >>> 	v_ac_res			ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 567: 1 проблем(ы)
-- >>> 	v_ac_res_a			ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 569: 1 проблем(ы)
-- >>> 	v_ac_res_p			ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 572: 1 проблем(ы)
-- >>> 	v_prc_dev	number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 573: 1 проблем(ы)
-- >>> 	v_r_ifrs	number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 574: 1 проблем(ы)
-- >>> 	v_f_ifrs	number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 575: 1 проблем(ы)
-- >>> 	v_ras_rvp	number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 581: 1 проблем(ы)
-- >>> 	li_cur_row := li_cur_row + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 598: 1 проблем(ы)
-- >>> 	v_acc_saldo := F.A('В' || P_ACC.[ARC_MOVE] || 'сН', P_DATE + 1);	-- Остаток на счёте задолженности
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 608: 1 проблем(ы)
-- >>> 					v_acc_priz_saldo_v := F.A('В' || v_acc_priz.[ARC_MOVE] || 'с',  P_DATE + 1);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 609: 1 проблем(ы)
-- >>> 					v_acc_priz_saldo   := F.A('В' || v_acc_priz.[ARC_MOVE] || 'сН', P_DATE + 1);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 651: 1 проблем(ы)
-- >>> 		v_ac_res_saldo := F.A('В' || v_ac_res.[ARC_MOVE] || 'сН', P_DATE + 1);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 663: 1 проблем(ы)
-- >>> 		v_ac_res_a_saldo := F.A('В' || v_ac_res_a.[ARC_MOVE] || 'СН', P_DATE + 1) * (-1);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 664: 1 проблем(ы)
-- >>> 		v_ac_res_p_saldo := F.A('В' || v_ac_res_p.[ARC_MOVE] || 'СН', P_DATE + 1);
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 683: 1 проблем(ы)
-- >>> 	if (P_ACC.[MAIN_V_ID] like '458%' or P_ACC.[MAIN_V_ID] like '47423%') and P_ACC.[NAME] like '%РКО%' then
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 688: 1 проблем(ы)
-- >>> 								when P_PROD%class = 'KRED_PERS' and P_ACC.[MAIN_USV].[NUM] like '459%'  then '2.3.2.  Проценты по кредитам ФЛ: - %% просроченные'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 690: 1 проблем(ы)
-- >>> 								when P_PROD%class = 'KRED_CORP' and P_ACC.[MAIN_USV].[NUM] like '459%'  then '2.3.2.  Проценты по кредитам ЮЛ: - %% просроченные'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 692: 1 проблем(ы)
-- >>> 								when P_PROD%class = 'OVERDRAFTS' and P_ACC.[MAIN_USV].[NUM] like '459%'  then '2.3.2.  Проценты по овердрафтам: - %% просроченные'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 695: 1 проблем(ы)
-- >>> 								when P_PROD%class = 'BANKS_LOANS' and P_ACC.[MAIN_USV].[NUM] like '325%'  then '2.3.1.  Проценты по МБК: - %% просроченные'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 710: 1 проблем(ы)
-- >>> 								when P_PROD is null and P_ACC.[MAIN_USV].[NUM] like '322%' then 'Операции РЕПО'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 714: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 721: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 728: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 730: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 732: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 734: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 740: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 746: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 748: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 749: 1 проблем(ы)
-- >>> 	&xl.put(li_cur_row, i, F.A('В' || P_ACC.[ARC_MOVE] || 'с',  P_DATE + 1)); -- Сумма задолженности (Актив)
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 750: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 752: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 754: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 756: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 758: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 760: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 762: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 764: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 810: 1 проблем(ы)
-- >>> 	i := i + 1;*/
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 812: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 814: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 818: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 823: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 825: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 827: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 829: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 831: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 835: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 837: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 839: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 841: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 843: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 845: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 847: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 854: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 857: 1 проблем(ы)
-- >>> 	if P_PROD is null and P_ACC.[NAME] like '%РКО%' then
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 890: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 892: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 894: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 896: 1 проблем(ы)
-- >>> 	i := i + 1;
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 903: 1 проблем(ы)
-- >>> procedure calc_kred(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 905: 1 проблем(ы)
-- >>> 	ac_res_r  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 906: 1 проблем(ы)
-- >>> 	ac_res_un ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 907: 1 проблем(ы)
-- >>> 	ac_res_a  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 908: 1 проблем(ы)
-- >>> 	ac_res_p  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 948: 1 проблем(ы)
-- >>> 			and res.[ACC](true) = ac
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 972: 1 проблем(ы)
-- >>> 		if (F.A('В' || ac.obj_ac.[ARC_MOVE] || 'сН', P_DATE + 1) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 973: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_r.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 974: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_un.[ARC_MOVE] || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 975: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_a.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 976: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_p.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 989: 1 проблем(ы)
-- >>> procedure calc_gar(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 991: 1 проблем(ы)
-- >>> 	ac_res_r  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 992: 1 проблем(ы)
-- >>> 	ac_res_un ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 993: 1 проблем(ы)
-- >>> 	ac_res_a  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 994: 1 проблем(ы)
-- >>> 	ac_res_p  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 995: 1 проблем(ы)
-- >>> 	v_res_p	  ref [RES_BASE_ACCS];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 996: 1 проблем(ы)
-- >>> 	v_sum_port number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 997: 1 проблем(ы)
-- >>> 	v_sum_ifrs_port number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 998: 1 проблем(ы)
-- >>> 	v_prev_port ref [RES_PORT];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


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


-- Строка 1049: 1 проблем(ы)
-- >>> 		if (F.A('В' || ac.obj_ac.[ARC_MOVE] || 'сН', P_DATE + 1) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1050: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_r.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1051: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_un.[ARC_MOVE] || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1052: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_a.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1053: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_p.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1075: 1 проблем(ы)
-- >>> procedure calc_mbk(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 1077: 1 проблем(ы)
-- >>> 	ac_res_r  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 1078: 1 проблем(ы)
-- >>> 	ac_res_a  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 1079: 1 проблем(ы)
-- >>> 	ac_res_p  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 1119: 1 проблем(ы)
-- >>> 			and res.[ACC](true) = ac
--   Проблема 1: v50.SQL.OUTERJOIN.п.1.1
--   Описание: Внешнее соединение через реквизит-ссылку с параметром true
--   Пример исправления: where cr.[LIST_PAY] = fo&collection(true)


-- Строка 1144: 1 проблем(ы)
-- >>> 		if (F.A('В' || ac.obj_ac.[ARC_MOVE] || 'сН', P_DATE + 1) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1145: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_r.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1146: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_a.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1147: 1 проблем(ы)
-- >>> 		   coalesce(F.A('В' || ac_res_p.[ARC_MOVE]  || 'сН', P_DATE + 1), 0) = 0
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1159: 1 проблем(ы)
-- >>> procedure calc_POT(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 1161: 1 проблем(ы)
-- >>> 	v_sum_port number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 1162: 1 проблем(ы)
-- >>> 	v_sum_ifrs_port number;
--   Проблема 1: v50.PROC.NATIVEID.п.3.26
--   Описание: Объявление NUMBER переменной


-- Строка 1163: 1 проблем(ы)
-- >>> 	v_prev_port ref [RES_PORT];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 1177: 1 проблем(ы)
-- >>> 		  	and port.[TYPE_RES].[NAME] not like 'ПОТ по экспресс-гарантиям%'
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: LIKE оператор (проверить тип поля)
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1203: 1 проблем(ы)
-- >>> procedure calc_other(P_DATE date)
--   Проблема 1: v50.STOR.DATE.п.2.2
--   Описание: Тип DATE
--   Пример исправления: p_date in date


-- Строка 1205: 1 проблем(ы)
-- >>> 	ac_res_a  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 1206: 1 проблем(ы)
-- >>> 	ac_res_p  ref [AC_FIN];
--   Проблема 1: v50.PROC.TYPING.п.3.11
--   Описание: REF объявление


-- Строка 1229: 1 проблем(ы)
-- >>> 		if F.A('В' || res.obj.[ACC].[ARC_MOVE] || 'сН', P_DATE + 1) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1230: 1 проблем(ы)
-- >>> 		   F.A('В' || res.obj.[RES_ACC].[ARC_MOVE] || 'сН', P_DATE + 1) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1231: 1 проблем(ы)
-- >>> 		   F.A('В' || ac_res_a.[ARC_MOVE] || 'сН', P_DATE + 1) = 0 and
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'


-- Строка 1232: 1 проблем(ы)
-- >>> 		   F.A('В' || ac_res_p.[ARC_MOVE] || 'сН', P_DATE + 1) = 0
--   Проблема 1: v50.SQL.CAST.п.1.5
--   Описание: Сложение строки с числом
--   Пример исправления: select * from t where numeric_column like '123%'

