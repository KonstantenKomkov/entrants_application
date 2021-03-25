# -*- coding: utf-8 -*-
# ABIT *YEAR*
db.define_table('t_const', Field('NAME', length=12), Field("TEXT", length=200), migrate=False)
db.define_table('s_region', Field('NAME', length=42), migrate=False)
db.define_table('s_country', Field('NAME', length=42), Field('BUDGET_RULE', 'integer'), migrate=False)
db.define_table('s_program_names', Field("NAME", length=200), migrate=False)
db.define_table('t_fo', Field('NAME'), migrate=False)
db.define_table('t_fac', Field('IS_PRIMARY', 'integer'), Field('NAME', length=80), migrate=False)
db.define_table('t_languages', Field('NAME', length=20), Field('CODE', 'integer'), migrate=False)
db.define_table("t_level_groups", migrate=False)
db.define_table('t_levels', Field("NAME", length=150), Field("LEVEL_GROUP", "reference t_level_groups"), Field("CODE"),
                migrate=False)
db.define_table('s_graduation_types', Field("NAME", length=50), migrate=False)
db.define_table('s_prepcourses', Field("NAME", length=40), migrate=False)
db.define_table('t_directions', Field("LEVEL", 'reference t_levels', rname='"LEVEL"'), Field("NAME", length=200),
                migrate=False)
db.define_table('s_document_types', Field("NAME", length=120), Field("USAGE_TYPE", "integer"), migrate=False)
db.define_table('t_disciplines', Field('NAME', length=70), Field("EXAMINATION_CATEGORY", 'integer'),
                Field("MIN_SCORE", "integer"), migrate=False)
db.define_table('s_kladr_loc_type', Field('NAME', length=50), Field('LEVEL', 'integer'),
                Field('ACTIVITY_INDEX', 'integer'), migrate=False)
db.define_table('s_achievements_group', migrate=False)
db.define_table('s_achievements', Field('NAME', length=100), Field('SCORES', 'decimal(5,1)'),
                Field('MAX_SCORES', 'decimal(5,1)'), Field('IS_ACTIVE', 'integer'),
                Field('ACHIEVEMENT_GROUP', 'reference s_achievements_group'), migrate=False)
db.define_table('s_classrooms', migrate=False)
db.define_table('t_exams_schedule', Field('DISC', 'integer'), Field('CLASSROOM', 'reference s_classrooms'),
                Field('EXAM_DATE', 'date'), Field('EXAM_TIME', 'time'), Field('NOTE', length=50),
                Field('OCCUPANCY', 'integer'), Field('CLOSED', 'integer'), migrate=False)
db.define_table('s_document_types_app', Field('DOC_TYPE', 'reference s_document_types'), Field('OBJ_CAT', 'integer'),
                Field('OBJ_ID', 'integer'), migrate=False)
db.define_table('t_admission_schedule', Field('FO', 'reference t_fo'), Field('LEVEL_GROUP', 'reference t_level_groups'),
                Field('BY_USE', 'integer'), Field('CONTRACT', 'integer'), Field('NAME', length=50),
                Field('BEGINNING', 'date'), Field('END_APP', 'date'), migrate=False)
db.define_table('t_admission_schedule_stages', Field('FO', 'integer'), Field('LEVEL_GROUP', 'integer'),
                Field('CONTRACT', 'integer'), Field('NUM', 'integer'), Field('PREFERENTIAL', 'integer'),
                Field('CERT_DATE', 'date'), Field('ORDER_DATE', 'date'), Field('END_TESTS', 'date'),
                Field('COMPETITIVE_LISTS', 'date'), migrate=False)
db.define_table('a_blocks_by_date', Field('BLOCK_TYPE', length=50), Field('FORBID_TO', 'datetime'), migrate=False)
db.define_table('a_persons', Field("EMAIL", length=40), migrate=False)
db.define_table('a_competition_groups', Field('FO', 'reference t_fo'), Field('FAC', 'reference t_fac'),
                Field('DIRECTION', 'reference t_directions'), Field('NAME', length=150), Field('FIS_ID', length=20),
                Field('BUDGET_PLACES', 'integer'), Field('CONTRACT_PLACES', 'integer'),
                Field('PREFERENTIAL_LIMIT', 'integer'), Field('TARGET_LIMIT', 'integer'), Field('FILE_NAME', length=30),
                Field('PRICE', 'decimal(8,2)'), Field('REQUIRE_HIGH_GRADUATION', 'integer'),
                Field('REQUIRE_PROFESSIONAL', 'integer'), Field('IGNORE_MON', 'integer'), Field('COURSE', 'integer'),
                Field('SPECIAL_LIMIT', 'integer'), Field('CG_GROUP', 'integer'), Field('DIR_SUBTYPE', 'integer'),
                Field('MON_TYPE', 'integer'), Field('PC_ID', length=10), Field('NEXT_WAVE_PLACES', 'integer'),
                Field('ID_1C', length=8), Field('PLAN_GROUPS_COUNT', 'integer'), Field('IS_EDU_MIN_SPECIAL', 'integer'),
                migrate=False)
db.define_table('t_competition_groups_exams', Field('COMPETITION_GROUP', 'reference a_competition_groups'),
                Field('DISC', 'reference t_disciplines'), Field('DISC_ORDER', 'integer'),
                primarykey=['COMPETITION_GROUP', 'DISC'], migrate=False)


# SQLITE3 INSIDE Application
db_app.define_table('doc_images', Field('person', label='ФИО', writable=False), Field('doctype', 'integer'),
                    Field('file', 'upload', label='Документ',
                          requires=[IS_UPLOAD_FILENAME(extension='^(pdf|tiff|png|bmp|jpeg|jpg)$'),
                                    IS_LENGTH(10485760, 1024)]), format='%(title)s')


# XMLCONTAINER.FDB
db_xml.define_table('xml_files', Field('F', length=25), Field('I', length=40), Field('O', length=25),
                    Field('IS_IMPORTED', 'integer'), Field('XML_FILE'), Field('BY_USE', 'integer'),
                    Field('IS_CORRECTION', 'integer'), migrate=False)
db_xml.define_table('bin_files', Field('PARENT', 'reference xml_files'), Field('SRC_FILENAME', length=200),
                    Field('FILE_DATA', 'blob'), migrate=False)
db_xml.define_table('xml_files_links', Field('XML_ID', 'reference xml_files'), Field('FILE_NAME', length=200),
                    Field('FILE_TYPE', 'integer'), primarykey=['XML_ID'], migrate=False)
db_xml.define_table('abit_validation_codes', Field('A_EMAIL', length=40), Field('V_CODE', 'integer'),
                    Field('SESSION_DATE', 'datetime'), Field('CONFIRMED', 'integer'), migrate=False)
db_xml.define_table('s_email_adress', Field('EMAIL_DOMEN', length=15), Field('EMAIL_LINK', length=30),
                    Field('EMAIL_NAME', length=10), migrate=False)
