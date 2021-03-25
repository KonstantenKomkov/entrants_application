#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *


@lazy_cache('total_information', time_expire=60 * 60 * 24, cache_model='ram')
def get_dictionaries():
    db = current.db
    all_countries = db().select(db.s_country.id, db.s_country.NAME, db.s_country.BUDGET_RULE)
    budget_countries_list = list()
    for row in all_countries:
        if row.BUDGET_RULE is not None:
            if row.BUDGET_RULE == 1:
                budget_countries_list.append(row.id)
    budget_countries_list_without_rf = budget_countries_list.copy()
    budget_countries_list_without_rf.remove(1)
    country = {rec.id: rec.NAME for rec in all_countries}
    region = {rec.id: rec.NAME for rec in db(db.s_region.NAME != 'Нет').select(db.s_region.id, db.s_region.NAME)}
    identity_document = {rec.id: rec.NAME for rec in db(
        (db.s_document_types.USAGE_TYPE == 1) & (db.s_document_types.id != 4) &
        (db.s_document_types.id != 11) & (db.s_document_types.id != 15) & (db.s_document_types.id != 16) &
        (db.s_document_types.id != 17)).select(db.s_document_types.id, db.s_document_types.NAME)}
    settlement_type = {rec.id: rec.NAME for rec in db(db.s_kladr_loc_type.LEVEL == 4).select(
        db.s_kladr_loc_type.id, db.s_kladr_loc_type.NAME, orderby=~db.s_kladr_loc_type.ACTIVITY_INDEX)}
    house_type = {rec.id: rec.NAME for rec in db(db.s_kladr_loc_type.LEVEL == 5).select(
        db.s_kladr_loc_type.id, db.s_kladr_loc_type.NAME, orderby=~db.s_kladr_loc_type.ACTIVITY_INDEX)}

    languages = {rec.id: rec.NAME for rec in db(db.t_languages.CODE != 643).select(db.t_languages.id,
                                                                                   db.t_languages.NAME)}
    courses = {rec.id: rec.NAME for rec in db(db.s_prepcourses).select(db.s_prepcourses.id, db.s_prepcourses.NAME,
                                                                       orderby=db.s_prepcourses.id)}
    diplomas_and_levels = db((db.s_document_types_app.OBJ_CAT == 6) & (db.s_document_types_app.DOC_TYPE != 33)).select(
        db.s_document_types.NAME, db.s_document_types_app.DOC_TYPE, db.s_document_types_app.OBJ_ID, db.t_levels.NAME,
        db.t_levels.CODE,
        join=[db.s_document_types.on(db.s_document_types_app.DOC_TYPE == db.s_document_types.id),
              db.t_levels.on(db.s_document_types_app.OBJ_ID == db.t_levels.id)])

    achievements = db(db.s_achievements.IS_ACTIVE > 0).select(
        db.s_achievements.NAME, db.s_achievements.SCORES, db.s_achievements.MAX_SCORES,
        db.s_achievements.ACHIEVEMENT_GROUP, orderby=db.s_achievements.MAX_SCORES)

    mag_achievements = list()
    bak_achievements = list()
    asp_achievements = list()
    for row in achievements:
        if row.ACHIEVEMENT_GROUP == 3:
            mag_achievements.append(row)
        elif row.ACHIEVEMENT_GROUP == 1:
            bak_achievements.append(row)
        else:
            asp_achievements.append(row)

    from_constants = db((db.t_const.NAME == 'RECTOR_RANKU') | (db.t_const.NAME == 'PREDSEDU') |
                        (db.t_const.NAME == 'VUZ')).select(db.t_const.NAME, db.t_const.TEXT)
    rector_rank, rector_name, vuz_name = '', '', ''
    for row in from_constants:
        if row.NAME == 'RECTOR_RANKU':
            rector_rank = row.TEXT
        elif row.NAME == 'PREDSEDU':
            rector_name = row.TEXT
        else:
            vuz_name = row.TEXT
    educations_form = {rec.id: rec.NAME for rec in db(db.t_fo.id != 4).select(db.t_fo.id, db.t_fo.NAME)}
    faculties = {rec.id: rec.NAME for rec in db(db.t_fac).select(db.t_fac.id, db.t_fac.NAME)}
    return {'country': country, 'region': region, 'identity_document': identity_document, 'vuz_name': vuz_name,
            'settlement_type': settlement_type, 'house_type': house_type, 'languages': languages, 'courses': courses,
            'diplomas_and_levels': diplomas_and_levels, 'bak_achievements': bak_achievements,
            'mag_achievements': mag_achievements, 'asp_achievements': asp_achievements, 'rector_rank': rector_rank,
            'rector_name': rector_name, 'educations_form': educations_form, 'faculties': faculties,
            'budget_countries_list': budget_countries_list,
            'budget_countries_list_without_rf': budget_countries_list_without_rf}


def create_information_form():
    T = current.T
    session = current.session
    dictionaries = get_dictionaries()
    country = dictionaries['country']
    region = dictionaries['region']
    identity_document = dictionaries['identity_document']
    settlement_type = dictionaries['settlement_type']
    house_type = dictionaries['house_type']

    form = FORM(
        LEGEND(),
        DIV(P(H4(T('Personal data')))),
        DIV(
            DIV(
                LABEL(f"{T('Surname')}:", _for='f'),
                INPUT(_type='text', _id='f', _name='f', _value=session.abit_f if session.abit_f else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value')),
                                IS_LENGTH(maxsize=25, error_message='Не более 25 символов')],
                      _class='form-control', _placeholder=T('Surname')), _class='col-md-4 mb-3'),
            DIV(
                LABEL(
                    f"{T('Name')}:", _for='i'),
                INPUT(_type='text', _id='i', _name='i', _value=session.abit_i if session.abit_i else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value')),
                                IS_LENGTH(maxsize=40, error_message='Не более 25 символов')],
                      # ,IS_MATCH("^[А-Яа-я]+$",error_message='Только кириллица')
                      _class='form-control', _placeholder=T('Name')), _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Middle name')}:", _for='o'),
                INPUT(_type='text', _id='o', _name='o', _value=session.abit_o if session.abit_o else '',
                      requires=[IS_LENGTH(maxsize=25, error_message='Не более 25 символов')],
                      _class='form-control', _placeholder=T('Middle name')), _class='col-md-4 mb-3'),
            _class='form-group row'),
        DIV(
            DIV(
                LABEL(f"{T('Country')}:", _for='country'),
                SELECT(*[OPTION(value_, _value=key_) for key_, value_ in iter(country.items())], _id='country',
                       _name='country', value=session.abit_country if session.abit_country else '',
                       _class='form-control', requires=IS_IN_SET(country.keys(), zero=T('choose one'),
                                                                 error_message='Выберите один из')),
                _class='col-md-4 mb-3'
            ),
            DIV(
                LABEL(f"{T('Phone')}:", _for='phone'),
                INPUT(_id='phone', _name='phone', _value=session.abit_phone if session.abit_phone else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))],
                      # , IS_MATCH("^[0-9.-]+$",error_message='Только цифры и тире')
                      _class='form-control', _placeholder=T('Phone')), _class='col-md-8'),
            _class='form-group row'),
        LEGEND(),
        DIV(P(H4(T('Identity document')))),
        DIV(
            DIV(
                LABEL(f"{T('Type of document')}:", _for='doc_type', ),
                SELECT(
                    *[OPTION(value_, _value=key_) for key_, value_ in iter(identity_document.items())], _id='doc_type',
                    _name='doc_type', _class='form-control',
                    value=session.abit_doc_type if session.abit_doc_type else '',
                    requires=IS_IN_SET(identity_document.keys(), zero=T('choose one'),
                                       error_message='Выберите один из')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Series')}:", _for='doc_ser'),
                INPUT(_id='doc_ser', _name='doc_ser', _value=session.abit_doc_ser if session.abit_doc_ser else '',
                      _class='form-control', _placeholder=T('Series')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Number')}:", _for='doc_num'),
                INPUT(_id='doc_num', _name='doc_num', _value=session.abit_doc_num if session.abit_doc_num else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))], _class='form-control', _placeholder=T('Number')),
                _class='col-md-4 mb-3'),
            _class='form-group row'),
        DIV(
            DIV(
                LABEL(f"{T('Is issued')}:", _for='doc_src'),
                INPUT(_id='doc_src', _name='doc_src', _value=session.abit_doc_src if session.abit_doc_src else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))], _class='form-control', _placeholder=T('Is issued')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Date of issue')} ({T('dd.mm.yyyy')}):", _for='doc_date'),
                INPUT(_type='date', _id='doc_date', _name='doc_date',
                      _value=session.abit_doc_date if session.abit_doc_date else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value')), IS_DATE()], _class='form-control'),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Division code')}:", _for='doc_kodp'),
                INPUT(_id='doc_kodp', _name='doc_kodp', _value=session.abit_doc_kodp if session.abit_doc_kodp else '',
                      _class='form-control',
                      _placeholder=T('Division code')),
                _class='col-md-4 mb-3'),
            _class='form-group row'),
        DIV(
            DIV(
                LABEL(f"{T('Birthplace')}:", _for='birthplace'),
                INPUT(_id='birthplace', _name='birthplace',
                      _value=session.abit_doc_place if session.abit_doc_place else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))], _class='form-control', _placeholder=T('Birthplace')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Birth date')} {T('dd.mm.yyyy')}:", _for='birthdate'),
                INPUT(_type='date', _id='birthdate', _name='birthdate',
                      _value=session.abit_doc_birthd if session.abit_doc_birthd else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value')), IS_DATE()], _class='form-control'),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Index of residence')}:", _for='doc_index'),
                INPUT(_id='doc_index', _name='doc_index',
                      _value=session.abit_doc_index if session.abit_doc_index else '', _class='form-control'),
                _class='col-md-4 mb-3'),
            _class='form-group row'),
        LEGEND(),
        DIV(P(H4(T('Registered address')))),
        DIV(
            DIV(
                LABEL(f"{T('Region')}:", _for='region'),
                SELECT(
                    *[OPTION(value_, _value=key_) for key_, value_ in iter(region.items())], _id='region',
                    _name='region', value=session.abit_region if session.abit_region else '', _class='form-control',
                    requires=IS_IN_SET(region.keys(), zero=T('choose one'), error_message='Выберите один из')),
                _class='col-md-4 mb-3', _id='colRegion'),
            DIV(
                LABEL(f"{T('Settlement type')}:", _for='settlementtype'),
                SELECT(
                    *[OPTION(value_, _value=key_) for key_, value_ in iter(settlement_type.items())],
                    _id='settlementtype', _name='settlementtype', _class='form-control',
                    value=session.abit_settlement_type if session.abit_settlement_type else '',
                    requires=IS_IN_SET(settlement_type.keys(), zero=T('choose one'), error_message='Выберите один из')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Settlement name')}:", _for='point'),
                INPUT(_id='point', _name='point', _value=session.abit_point if session.abit_point else '',
                      _class='form-control', requires=[IS_NOT_EMPTY(T('Enter a value'))],
                      _placeholder=T('Settlement name')), _class='col-md-4 mb-3'), _class='form-group row'),
        DIV(
            DIV(
                LABEL(f"{T('District')}:", _for='district'),
                INPUT(_id='district', _name='district', _value=session.abit_district if session.abit_district else '',
                      _placeholder=T('District'), _class='form-control'), _class='col-md-4 mb-3'),
            DIV(
                LABEL('Тип объекта адресации дома:', _for='housetype'),
                SELECT(*[OPTION(value_, _value=key_) for key_, value_ in iter(house_type.items())], _id='housetype',
                       _name='housetype', _class='form-control',
                       value=session.abit_house_type if session.abit_house_type else '',
                       requires=IS_IN_SET(house_type.keys(), zero=T('choose one'),
                                          error_message='Выберите один из')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL('Название объекта адресации дома:', _for='street'),
                INPUT(_id='street', _name='street', _value=session.abit_street if session.abit_street else '',
                      _placeholder='имя', _class='form-control', requires=[IS_NOT_EMPTY(T('Enter a value'))]),
                _class='col-md-4 mb-3'), _class='form-group row'),
        DIV(
            DIV(
                LABEL(f"{T('House')}:", _for='house'),
                INPUT(_id='house', _name='house', _value=session.abit_house if session.abit_house else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))], _class='form-control', _placeholder=T('House')),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Body')}:", _for='case'),
                INPUT(_id='case', _name='case', _value=session.abit_case if session.abit_case else '',
                      _placeholder=T('Body'), _class='form-control'), _class='col-md-4 mb-3'),
            DIV(
                LABEL(f"{T('Flat')}:", _for='flat'),
                INPUT(_id='flat', _name='flat', _value=session.abit_flat if session.abit_flat else '',
                      _placeholder=T('Flat'), _class='form-control'), _class='col-md-4 mb-3'),
            _class='form-group row'),
        DIV(
            DIV(
                INPUT(_value=T('Next'), _type='submit', _class='good-btn w-100', _id='next'), _class='col center mb-3'),
            _class='form-group row'),
        INPUT(_type='number', _id='link_number', _name='link_number', _class='d-none'),
        _id="form1")
    return form


def create_educational_form(level, c):
    # c = 0 (bak), c = 1 (mag)
    import datetime
    T = current.T
    session = current.session

    dictionaries = get_dictionaries()
    courses = dictionaries['courses']
    languages = dictionaries['languages']
    region = dictionaries['region']

    if c == 0:
        diplomas_set = list()
        diplomas_and_levels = dictionaries['diplomas_and_levels']
        for row in diplomas_and_levels:
            if row.t_levels.CODE < 6:
                diplomas_set.append(row.s_document_types_app.DOC_TYPE)
        diplomas_set = list(set(diplomas_set))
        ta_school_name = TEXTAREA(_id='eduName', _name='name', _rows=1, _class='form-control',
                                  value=session.edu_name if session.edu_name else '',
                                  requires=[IS_NOT_EMPTY(T('Enter a value'))])
        diploma = DIV(
            LABEL(f"{T('Education certificate')}:", _for='docsedu'),
            SELECT(_class='form-control', _id='docsedu', _name='docsedu',
                   value=session.edu_docsedu if session.edu_docsedu else '',
                   requires=IS_IN_SET(diplomas_set, zero=T('choose one'), error_message='Select value from list')),
            _class='col-md-4 mb-3 d-flex flex-column justify-content-between d-none',
            _id='eduDocument')
    else:
        ta_school_name = DIV(
            DIV(
                SPAN(DIV(_class='glyphicon-rgau'), _class='input-group-text form-edu-span', _id='our_graduate'),
                _class='input-group-prepend'),
            TEXTAREA(_id='vuzName', _name='name', _rows=1, _class='form-control',
                     value=session.edu_name if session.edu_name else '', requires=[IS_NOT_EMPTY(T('Enter a value'))]),
            _class='input-group mb-3')
        diploma = ''

    form = FORM(
        LEGEND(),
        DIV(P(H4(T('education').capitalize()))),
        DIV(
            DIV(
                LABEL('{0}:'.format(T("education's level")).capitalize(), _for='level', ),
                SELECT(
                    *[OPTION(value_, _value=key_) for key_, value_ in iter(level.items())],
                    _class='form-control align-items-end', value=session.edu_lvl if session.edu_lvl else '',
                    _name='lvl', _id='level'),
                _class='col-md-4 mb-3 d-flex flex-column justify-content-between'),
            diploma,
            DIV(
                LABEL(f"{T('Region')} учебного заведения:", _for='region'),
                SELECT(
                    *[OPTION(value_, _value=key_) for key_, value_ in iter(region.items())], _id='region',
                    _name='region', value=session.edu_region if session.edu_region else '', _class='form-control',
                    requires=IS_IN_SET(region.keys(), zero=T('choose one'), error_message='Выберите один из')),
                _class='col-md-4 mb-3 d-flex flex-column justify-content-between', _id='colRegion'),
            DIV(
                LABEL('{0}:'.format(T("previous school adress (only district)")).capitalize(), _for='adr', ),
                INPUT(_id='adr', _name='adr', _class='form-control align-items-end',
                      value=session.edu_adr if session.edu_adr else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))]),
                _class='col-md-4 mb-3 d-flex flex-column justify-content-between'),
            DIV(
                LABEL('{0}:'.format(T("year of graduation")).capitalize(), _for='edu_year', ),
                INPUT(_class='form-control align-items-end', _name='year', _id='edu_year',
                      _value=session.edu_year if session.edu_year else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value')),
                                IS_INT_IN_RANGE(1950, current.request.now.year + 1,
                                                error_message=f'Год должен быть в диапозоне от 1950 до '
                                                              f'{current.request.now.year}')]),
                _class='col-md-4 mb-3 d-flex flex-column justify-content-between'),
            DIV(
                LABEL('{0}:'.format(T("series and number of the educational document")).capitalize(), _for='att', ),
                INPUT(_class='form-control align-items-end', _name='att', _id='att',
                      _value=session.edu_att if session.edu_att else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value'))]),
                _class='col-md-4 mb-3 d-flex flex-column justify-content-between'),
            DIV(
                LABEL('{0} {1}:'.format(T("date of issuance").capitalize(), T("dd.mm.yyyy")), _for='att_date', ),
                INPUT(_type='date', _name='att_date', _id='att_date',
                      _value=session.edu_att_date if session.edu_att_date else '',
                      requires=[IS_NOT_EMPTY(T('Enter a value')),
                                IS_DATE_IN_RANGE(format=T('%Y-%m-%d'), minimum=datetime.date(1950, 1, 1),
                                                 maximum=datetime.date(current.request.now.year, 11, 1),
                                                 error_message=f'Дата в диапазоне от 1950 до '
                                                               f'{current.request.now.year}')],
                      _class='form-control align-items-end'),
                _class='col-md-4 mb-3 d-flex flex-column justify-content-between'),
            _class='form-group row'),
        DIV(
            DIV(
                LABEL('{0}:'.format(T("previous school name")).capitalize(), _for='vuzName', ),
                ta_school_name,
                _class='col-md-12'),
            _class='form-group row'),
        LEGEND(),
        DIV(P(H4(T('other').capitalize()))),
        DIV(
            DIV(
                LABEL('{0}:'.format(T("access course")).capitalize(), _for='course', ),
                SELECT(*[OPTION(value_, _value=key_) for key_, value_ in iter(courses.items())], _class='form-control',
                       value=session.edu_course if session.edu_course else '', _name='course', _id='course'),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL('{0}:'.format(T("foreign language")).capitalize(), _for='edu_language', ),
                SELECT(*[OPTION(value_, _value=key_) for key_, value_ in iter(languages.items())],
                       _class='form-control', _name='edu_language',
                       value=session.edu_language if session.edu_language else '', _id='edu_language'),
                _class='col-md-4 mb-3'),
            DIV(
                INPUT(_type='checkbox', _id='army', _name='army', _value=1, value=session.abit_army,
                      _class='form-check-input chb-size'),
                LABEL(T("service in army").capitalize(), _class='form-check-label chb-label', _for='army'),
                _class='col-md-4 mb-3 form-check text-center chb-optimaize'),
            _class='form-group row'),
        DIV(
            DIV(
                DIV(INPUT(_type='checkbox', _id='hostel', _name='hostel', _value=1, value=session.abit_hostel,
                          _class='align-self-center form-check-input agreement-chb mt-0')),
                DIV(P(T("I need a hostel for the duration of training"), _class='paragraf statement mb-0'),
                    _for='hostel'),
                _class="d-inline-flex justify-content-start my-3 px-3 w-100"),
            _class='form-group row'),
        DIV(
            DIV(
                INPUT(_value=T('Next'), _type='submit', _class='good-btn w-100', _id='next'),
                _class='col center mb-3'),
            _class='form-group row'),
        INPUT(_type='number', _id='link_number', _name='link_number', _class='d-none'))
    return form


def get_all_cg(level_group):
    db = current.db
    all_cg = db.executesql(
        f'SELECT CG.id AS CG_ID, CG.FO, CG.FAC, CG.DIRECTION AS DIR_ID, CG.NAME AS CG_NAME, CG.BUDGET_PLACES,'
        f'CG.CONTRACT_PLACES, CG.MIN_SUM, D.NAME AS DIR_NAME, PS.NAME AS PR_NAME,'
        f'(SELECT MAX(END_APP) FROM T_ADMISSION_SCHEDULE A2 WHERE A2.FO=CG.FO AND A2.LEVEL_GROUP=L.LEVEL_GROUP) AS '
        f'END_DATE, P.id AS P_ID FROM A_PROGRAMMS P '
        f'INNER JOIN A_COMPETITION_GROUPS CG ON CG.ID=P.COMP_GROUP '
        f'INNER JOIN S_PROGRAM_NAMES PS ON (P.NAME_ID=PS.ID) '
        f'INNER JOIN T_DIRECTIONS D ON D.ID=CG.DIRECTION '
        f'INNER JOIN T_LEVELS L ON (D."LEVEL"=L.ID) '
        f'WHERE CG.FO!=4 AND L.LEVEL_GROUP={db._adapter.dialect.quote(level_group)} '
        f'ORDER BY CG.FO, CG.FAC, D.NAME, CG.NAME, PS.NAME', as_dict=True)
    return all_cg


def create_json(all_cg):
    import datetime


    options = ''
    first = True
    fo = fac = direction = cg = -1
    for b in all_cg:
        if datetime.datetime.now().date() > b.get('END_DATE'):
            continue
        if first:
            options = f'{{"fo":"{b.get("FO")}","fac":[{{"fName":"{b.get("FAC")}","dir":[{{"dirName":"' \
                      f'{b.get("DIR_NAME")}","cg":[{{"cgName":"{b.get("CG_NAME")}","minSum":"{b.get("MIN_SUM")}",' \
                      f'"pr":["{b.get("PR_NAME")}",'
            fo = b.get('FO')
            fac = b.get('FAC')
            direction = b.get('DIR_ID')
            cg = b.get('CG_NAME')
            first = False
        else:
            if fo != b.get('FO'):
                options = options[0:-1]
                options = f'{options}]}}]}}]}}]}},{{"fo":"{b.get("FO")}","fac":[{{"fName":"{b.get("FAC")}","dir":' \
                          f'[{{"dirName":"{b.get("DIR_NAME")}","cg":[{{"cgName":"{b.get("CG_NAME")}","minSum":' \
                          f'"{b.get("MIN_SUM")}","pr":["{b.get("PR_NAME")}",'
                fo = b.get('FO')
                fac = b.get('FAC')
                direction = b.get('DIR_ID')
                cg = b.get('CG_NAME')
            else:
                if fac != b.get('FAC'):
                    options = options[0:-1]
                    options = f'{options}]}}]}}]}},{{"fName":"{b.get("FAC")}","dir":[{{"dirName":"' \
                              f'{b.get("DIR_NAME")}","cg":[{{"cgName":"{b.get("CG_NAME")}","minSum":"' \
                              f'{b.get("MIN_SUM")}","pr":["{b.get("PR_NAME")}",'
                    fac = b.get('FAC')
                    direction = b.get('DIR_ID')
                    cg = b.get('CG_NAME')
                else:
                    if direction != b.get('DIR_ID'):
                        options = options[0:-1]
                        options = f'{options}]}}]}},{{"dirName":"{b.get("DIR_NAME")}","cg":[{{"cgName":"' \
                                  f'{b.get("CG_NAME")}","minSum":"{b.get("MIN_SUM")}","pr":["{b.get("PR_NAME")}",'
                        direction = b.get('DIR_ID')
                        cg = b.get('CG_NAME')
                    else:
                        if cg != b.get('CG_NAME'):
                            options = options[0:-1]
                            options = f'{options}]}},{{"cgName":"{b.get("CG_NAME")}","minSum":"{b.get("MIN_SUM")}",' \
                                      f'"pr":["{b.get("PR_NAME")}",'
                            cg = b.get('CG_NAME')
                        else:
                            options = f'{options}"{b.get("PR_NAME")}",'
    options = options[0:-1]
    options = f'[{options}]}}]}}]}}]}}]'
    return options


def show_loaded_documents(files_names, id_element, document_errors=''):
    document_types = {1: 'identityDoc', 2: 'educationalDoc', 3: 'achievementsDoc', 4: 'otherDoc', 5: 'photoDoc',
                      20: 'liner'}
    if files_names:
        html = f'{document_errors}<div id="{document_types[id_element]}" class="row">'
        for i in files_names:
            s = i[len(i) - 5:len(i)]
            if (s.find('.jpg') > -1) or (s.find('.JPG') > -1) or (s.find('.jpeg') > -1) or (s.find('.JPEG') > -1) or \
                    (s.find('.png') > -1) or (s.find('.PNG') > -1) or (s.find('.bmp') > -1) or (s.find('.BMP') > -1):
                html = f'{html}<div class="col py-3"><div class="document"><p class="text-center text-success ' \
                       f'expansion">файл загружен</p></div></div>'
            elif (s.find('.pdf') > -1) or (s.find('.PDF') > -1):
                html = f'{html}<div class="col py-3"><div class="document"><p class="text-center text-success ' \
                       f'expansion">.pdf загружено</p></div></div>'
            elif (s.find('.tif') > -1) or (s.find('.TIF') > -1):
                html = f'{html}<div class="col py-3"><div class="document"><p class="text-center text-success ' \
                       f'expansion">.tiff загружено</p></div></div>'
        html = f'{html}</div>'
    else:
        html = f'{document_errors}'
    return XML(html)


def load_document(document, f, i, number, email):
    db_app = current.db_app
    m = 0
    document_types = {1: 'identityDoc', 2: 'educationalDoc', 3: 'achievementsDoc', 4: 'otherDoc', 5: 'photoDoc',
                      20: 'liner'}
    files_names = list()
    if document is not None:
        if document.doctype is not None:
            document_errors = f'<div class="row" id="{document_types[int(document.doctype)]}-errors">'
            for key in document:
                if key != 'doctype':
                    last_symbol = len(document[key].filename) - 1
                    while document[key].filename[last_symbol] != '.':
                        last_symbol -= 1
                    without_ext = document[key].filename[:last_symbol]
                    if len(without_ext) < 35:
                        load = db_app.doc_images.validate_and_insert(person=f'{f} {i} {number} {email}',
                                                                     doctype=document.doctype, file=document[key])
                        if load.errors is not None:
                            for x in load.errors.as_dict().values():
                                if x == 'Enter from 1024 to 1.04858e+07 characters':
                                    document_errors = f'{document_errors}<div class="col"><p class="error">Загрузите' \
                                                      f' файл размером менее 10MB</p></div>'
                                else:
                                    document_errors = f'{document_errors}<div class="col"><p class="error">{x}</p>' \
                                                      f'</div>'
                                m += 1
                        if m == 0:
                            files_names.append(document[key].filename)
                    else:
                        m += 1
                        document_errors = f'{document_errors}<div class="col"><p class="error">Имя файла должно быть' \
                                          f' < 35 cимволов</p></div>'
            if m > 0:
                document_errors = f'{document_errors}</div>'
            else:
                document_errors = ''
            return show_loaded_documents(files_names, int(document.doctype), document_errors)


def xml_escape(s):
    if isinstance(s, str):
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        s = s.replace('&', '&amp;')
        s = s.replace("'", '&apos;')
        s = s.replace('"', '&quot;')
        return s
    else:
        return s


def agreement_form(c, year):
    T = current.T
    session = current.session
    chb_error_message = 'Если какой-либо пункт соглашения Вас не устраивает, воздержитесь от отправки заявления.'
    if c == 0:
        budget_agreement = ('Подтверждаю отсутствие диплома бакалавра, диплома специалиста, диплома магистра при '
                            'поступлении на обучение на места в рамках контрольных цифр.')
        count_agreements = DIV(
            INPUT(_type="checkbox", _name="count-universities", _id="count-universities", _value="1",
                  value=session.count_universities_agreement, _class="form-check-input agreement-chb",
                  requires=IS_NOT_EMPTY(error_message=chb_error_message)),
            P(('Подтверждаю одновременную подачу заявлений не более чем в пять организаций высшего образования, '
               'включая РГАУ-МСХА имени К.А. Тимирязева.'), _class="paragraf statement"),
            INPUT(_type="checkbox", _name="count-cg", _id="count-cg", _value="1", value=session.count_cg_agreement,
                  _class="form-check-input agreement-chb", requires=IS_NOT_EMPTY(error_message=chb_error_message)),
            P(('Подтверждаю одновременную подачу заявлений о приеме по результатам конкурса не более, чем по трем '
               'направлениям подготовки/специальностям в РГАУ-МСХА имени К.А. Тимирязева.'),
              _class="paragraf statement"))
    elif c == 1:
        budget_agreement = ('Подтверждаю отсутствие диплома специалиста, диплома магистра при поступлении на обучение '
                            'на места в рамках контрольных цифр.')
        count_agreements = DIV()
    else:
        budget_agreement = ('Подтверждаю отсутствие диплома об окончании аспирантуры (адъюнктуры) или диплома кандидата'
                            ' наук - при поступлении на обучение на места в рамках контрольных цифр.')
        count_agreements = DIV()

    form = FORM(
        DIV(
            DIV(
                INPUT(_type="checkbox", _name="license", _id="license", _value="1", value=session.agreement_license,
                      _class="form-check-input agreement-chb", requires=IS_NOT_EMPTY(error_message=chb_error_message)),
                P(XML(f'С <a href="http://old.timacad.ru/about/history/status/lizenzia27102014.pdf" target="_blank" '
                      f'rel="noreferrer">копией лицензии</a> на право осуществления образовательной деятельности (<a '
                      f'href="http://www.fdp.timacad.ru/abitur/licence/licence.php" target="_blank" rel="noreferrer">'
                      f'с приложениями</a>), серия 90Л01 № 00080764, рег. № 1099 от 10.10.2014 г., <a href="'
                      f'http://old.timacad.ru/about/history/status/accreditation.pdf" target="_blank" rel="'
                      f'noreferrer">копией свидетельства</a> о государственной аккредитации серия 90А01 № 0001329, '
                      f'рег. № 1250 от 09.04.2015 г., Порядком приема в высшие учебные заведения РФ, Правилами приема '
                      f'в РГАУ-МСХА имени К.А. Тимирязева на {str(year)} - {str(year + 1)} '
                      f'учебный год, с информацией о предоставляемых поступающим особых правах и преимуществах при '
                      f'приеме на обучение по программам бакалавриата и программам специалитета, с правилами подачи '
                      f'апелляции по результатам вступительных испытаний, проводимых университетом  самостоятельно '
                      f'опубликованными на сайте «<a href="http://www.fdp.timacad.ru/abitur/" target="_blank" rel="'
                      f'noreferrer">Абитуриенту {str(year)}</a>» ознакомлен(-а).'),
                  _class="paragraf statement"),
                INPUT(_type="checkbox", _name="budget", _id="budget", _value="1", value=session.agreement_budget,
                      _class="form-check-input agreement-chb", requires=IS_NOT_EMPTY(error_message=chb_error_message)),
                P(budget_agreement, _class="paragraf statement"),
                INPUT(_type="checkbox", _name="personal-data", _id="personal-data", _value="1",
                      value=session.agreement_personal_data, _class="form-check-input agreement-chb",
                      requires=IS_NOT_EMPTY(error_message=chb_error_message)),
                P(('Согласен(-а) на обработку моих персональных данных в порядке, установленном Федеральным законом от '
                   '27.07.2006 г. ФЗ № 152-ФЗ «О персональных данных».'), _class="paragraf statement"),
                count_agreements,
                INPUT(_type="checkbox", _name="original", _id="original", _value="1", value=session.agreement_original,
                      _class="form-check-input agreement-chb",
                      requires=IS_NOT_EMPTY(error_message=chb_error_message)),
                P(('С датами завершения представления оригинала документа об образовании установленного образца и '
                   'заявления о согласии на зачисление на каждом этапе ознакомлен(-а).'), _class="paragraf statement"),
                INPUT(_type="checkbox", _name="reliability", _id="reliability", _value="1",
                      value=session.agreement_reliability, _class="form-check-input agreement-chb",
                      requires=IS_NOT_EMPTY(error_message=chb_error_message)),
                P(('Ознакомлен(-а) с информацией об ответственности за достоверность сведений, указанных в заявлении о '
                   'приёме, и за подлинность документов, подаваемых для поступления.'), _class="paragraf statement"),
                _class='col'), _class='form-group row'),
        DIV(
            DIV(
                H4('Доступ к личному кабинету абитуриента'),
                P(('Доступ к личному кабинету будет открыт после проверки Вашего заявления оператором. Используйте '
                   'надёжный пароль!'), _class="paragraf statement"), _class='col'), _class='form-group row'),
        DIV(
            DIV(
                LABEL('Пароль:', _for='abit_pass', ),
                INPUT(_type='password', _id='abit_pass', _name='abit_pass', _class='form-control',
                      requires=[IS_NOT_EMPTY('Введите значение'),
                                IS_LENGTH(minsize=8, error_message=T('The minimum length is 8 characters')), CRYPT()]),
                _class='col-md-4 mb-3'),
            DIV(
                LABEL('Повторите пароль:', _for='abit_r_pass', ),
                INPUT(_type='password', _class='form-control', _name='abit_r_pass', _id='abit_r_pass',
                      requires=[IS_NOT_EMPTY('Введите значение'),
                                IS_EQUAL_TO(current.request.vars.abit_pass, error_message='Пароли должны совпадать!'),
                                CRYPT()]), _class='col-md-4 mb-3'), _class='form-group row'),
        DIV(
            DIV(
                P('Отправить заявление оператору?', _class='statement text-center'), _class='col'),
            _class='form-group row'),
        DIV(
            DIV(
                TAG.BUTTON(DIV(SPAN(_class='glyphicon glyphicon-send'), P('Отправить', _class='p-btn'),
                           _class='my-btn-conteiner'), _value='Далее', _id="edu", _type='submit',
                           _class='good-btn w-100'), _class='col center mb-3'), _class='form-group row'))
    return form


def delete_superfluous_cg(session_list, all_cg):
    superfluous_cg = list()
    for cg in session_list:
        for c_g in all_cg:
            if int(cg['cg_id']) == c_g['CG_ID']:
                break
        else:
            superfluous_cg.append(cg)
    for x in superfluous_cg:
        session_list.remove(x)
    return session_list


def clear_session():
    session = current.session
    s = ['abit_f', 'bit_i', 'abit_o', 'abit_phone', 'abit_email', 'abit_doc_ser', 'abit_doc_num', 'abit_doc_src',
         'abit_doc_date', 'abit_doc_kodp', 'abit_doc_index', 'abit_doc_place', 'abit_doc_birthd', 'abit_doc_type',
         'abit_doc_type_name', 'abit_country', 'cur_fo', 'cur_fac', 'cur_dir', 'cur_prog', 'abit_disc1', 'abit_mark1',
         'abit_disc2', 'abit_mark2', 'abit_disc3', 'abit_mark3', 'abit_disc4', 'abit_mark4', 'abit_disc5', 'abit_mark5',
         'abit_registration1', 'abit_registration2', 'abit_registration3', 'abit_registration4', 'abit_registration5',
         'abit_region', 'abit_district', 'abit_settlement_type', 'abit_s_type', 'abit_point', 'abit_house_type',
         'abit_h_type', 'abit_street', 'abit_house', 'abit_case', 'abit_flat', 'edu_lvl', 'edu_name', 'edu_year',
         'edu_adr', 'edu_docsedu', 'edu_docsedu_name', 'edu_att', 'edu_att_date', 'edu_course', 'edu_course_name',
         'edu_language', 'edu_language_name', 'abit_army', 'abit_hostel', 'agreement_zero', 'agreement_one',
         'agreement_two', 'agreement_three', 'agreement_four', 'agreement_five', 'agreement_six', 'abit_comment',
         'exam_date_1', 'exam_date_2', 'exam_date_4', 'exam_date_5', 'exam_name_1', 'exam_name_2', 'exam_name_3',
         'exam_name_4', 'exam_name_5', 'abit_disc6', 'abit_mark6', 'abit_registration6', 'withoutege', 'egedocument',
         'ege_doc_type', 'ege_s', 'ege_n', 'ege_date', 'ege_code', 'ege_doc_issued', 'edu_region', 'ege_year1',
         'ege_year2', 'ege_year3', 'ege_year4', 'ege_year5', 'ege_year6']
    for x in s:
        session[x] = None
    session.prog_list = list()
