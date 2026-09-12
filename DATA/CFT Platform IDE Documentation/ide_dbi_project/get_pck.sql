select 'VER2' c from dual
union all
select '' c from dual
union all
select
	case s.obj_type
		when 'ТБП' then 'TYPE ' || s.obj_class_id
		when 'Операция' then 'METH ' || s.obj_class_id || ' ' || s.obj_short_name
		when 'Представление' then 'CRIT ' || s.obj_class_id || ' ' || s.obj_short_name
	end c
from (
/*
  Это копия VW_CRIT_PSH_LOCAL_OBJECTS "[ПСБ] Список локальных объектов"
*/
		select  a1.ID as OBJ_ID, 'ТБП' as OBJ_TYPE, a1.ID as OBJ_CLASS_ID, null as OBJ_SHORT_NAME, a1.NAME as OBJ_CLASS_NAME, null as OBJ_NAME, null as METH_TYPE, null as OBJ_CREATE_DATE, null as OBJ_CREATOR, a1.MODIFIED as OBJ_EDIT_DATE, null as OBJ_EDITOR, null as OBJ_DATE_USED, null as OBJ_USER_LAST, null as ISCALLEDBYMETHOD, case when  exists (
			select  c1.SUBJ_ID as SUBJ_ID, c1.OBJ_ID as OBJ_ID, c1.NOT_IN_MENU as NOT_IN_MENU
			from CLASS_RIGHTS c1
			where c1.OBJ_ID = a1.ID
		) then 'Да' else 'Нет' end as ISACCESSED, null as OBJ_USER_DR, null as OBJ_STATUS
		from CLASSES a1
		where not  exists (
			select  1 as A$1
			from OBJECTS_OPTIONS b1
			where b1.OBJ_TYPE = 'CLASSES' and b1.CLASS_ID = a1.ID
		)
		union all
		select  d1.ID as OBJ_ID, 'Операция' as OBJ_TYPE, e1.ID as OBJ_CLASS_ID, d1.SHORT_NAME as OBJ_SHORT_NAME, e1.NAME as OBJ_CLASS_NAME, d1.NAME as OBJ_NAME, DECODE(d1.FLAGS,'C','Добавить (конструктор)','Y','Удалить (деструктор)','M','Простая','S','Групповая','R','Отчет','O','Выбор','L','Библиотека','P','Печать','G','Списочная','Z','Фильтр','D','Копирование','A','Функ. реквизит',null) as METH_TYPE, d1.CREATED as OBJ_CREATE_DATE, d1.USER_CREATED as OBJ_CREATOR, d1.MODIFIED as OBJ_EDIT_DATE, d1.USER_MODIFIED as OBJ_EDITOR, (
			select  MAX(g1.C_DATE_START) as A$1
			from Z#PSH_LOCAL_CALLS g1
			where g1.C_ID_ACT = d1.ID
		) as OBJ_DATE_USED, (
			select  MAX(h2.C_NAME) keep (dense_rank last order by h1.C_DATE_START)  as A$1
			from Z#USER h2, Z#PSH_LOCAL_CALLS h1
			where h1.C_USER=h2.id(+)
			  and (h1.C_ID_ACT = d1.ID)
		) as OBJ_USER_LAST, case when  exists (
			select  i1.REFERENCING_ID as REFERENCING_ID, i1.REFERENCING_TYPE as REFERENCING_TYPE, i1.REFERENCED_ID as REFERENCED_ID, i1.REFERENCED_TYPE as REFERENCED_TYPE, i1.REFERENCED_QUAL as REFERENCED_QUAL, i1.REFS_COUNT as REFS_COUNT
			from DEPENDENCIES i1
			where i1.REFERENCED_ID = d1.ID and i1.REFERENCING_ID <> i1.REFERENCED_ID
		) then 'Да' else 'Нет' end as ISCALLEDBYMETHOD, case when  exists (
			select  j1.SUBJ_ID as SUBJ_ID, j1.OBJ_ID as OBJ_ID, j1.CLASS_ID as CLASS_ID
			from METHOD_RIGHTS j1
			where j1.OBJ_ID = d1.ID
		) then 'Да' else 'Нет' end as ISACCESSED, case when d1.USER_DRIVEN = 1 then 'Да' else 'Нет' end as OBJ_USER_DR, d1.STATUS as OBJ_STATUS
		from CLASSES e1, METHODS d1
		where e1.ID = d1.CLASS_ID and d1.FLAGS not in ('Z','A') and e1.ID not in ('CALC_PARAMS','CONV_57','CONV_APPL') and not  exists (
			select  1 as A$1
			from OBJECTS_OPTIONS f1
			where f1.OBJ_TYPE = 'METHODS' and f1.CLASS_ID = e1.ID and f1.SHORT_NAME = d1.SHORT_NAME
		)
		union all
		select  k1.ID as OBJ_ID, 'Представление' as OBJ_TYPE, l1.ID as OBJ_CLASS_ID, k1.SHORT_NAME as OBJ_SHORT_NAME, l1.NAME as OBJ_CLASS_NAME, k1.NAME as OBJ_NAME, null as METH_TYPE, null as OBJ_CREATE_DATE, null as OBJ_CREATOR, k1.MODIFIED as OBJ_EDIT_DATE, null as OBJ_EDITOR, (
			select  MAX(n1.C_DATE_START) as A$1
			from Z#PSH_LOCAL_CALLS n1
			where n1.C_ID_ACT = k1.ID
		) as OBJ_DATE_USED, (
			select  MAX(o2.C_NAME) keep (dense_rank last order by o1.C_DATE_START)  as A$1
			from Z#USER o2, Z#PSH_LOCAL_CALLS o1
			where o1.C_USER=o2.id(+)
			  and (o1.C_ID_ACT = k1.ID)
		) as OBJ_USER_LAST, null as ISCALLEDBYMETHOD, case when  exists (
			select  p1.SUBJ_ID as SUBJ_ID, p1.OBJ_ID as OBJ_ID, p1.CLASS_ID as CLASS_ID, p1.IMPLICIT as IMPLICIT, p1.TO_PRINTER as TO_PRINTER, p1.TO_FILE as TO_FILE
			from CRITERIA_RIGHTS p1
			where p1.OBJ_ID = k1.ID
		) then 'Да' else 'Нет' end as ISACCESSED, null as OBJ_USER_DR, (
			select  q1.STATUS as A$1
			from ALL_OBJECTS q1
			where q1.OBJECT_TYPE = 'VIEW' and q1.OBJECT_NAME = k1.SHORT_NAME
		) as OBJ_STATUS
		from CLASSES l1, CRITERIA k1
		where l1.ID = k1.CLASS_ID and not  exists (
			select  1 as A$1
			from OBJECTS_OPTIONS m1
			where m1.OBJ_TYPE = 'CRITERIA' and m1.CLASS_ID = l1.ID and m1.SHORT_NAME = k1.SHORT_NAME
		)
) s
