# -*- coding: utf-8 -*-
import datetime
import json
import bak_and_mag

interval = db().select(db.t_admission_schedule.BEGINNING, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()

date_close_app_form_bak = db((db.t_admission_schedule_stages.FO == 1) &
                             (db.t_admission_schedule_stages.LEVEL_GROUP == 1) &
                             (db.t_admission_schedule_stages.CONTRACT == 0) &
                             (db.t_admission_schedule_stages.NUM == 2) &
                             (db.t_admission_schedule_stages.PREFERENTIAL == 0)).select(
    db.t_admission_schedule_stages.CERT_DATE, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()

block = db(db.a_blocks_by_date.BLOCK_TYPE == 'FORBID_WEB_APP').select(db.a_blocks_by_date.FORBID_TO,
                                                                      cache=(cache.ram, 60 * 5), cacheable=True).first()
if (datetime.datetime.now().date() < interval.BEGINNING) | \
        (datetime.datetime.now().date() > date_close_app_form_bak.CERT_DATE):
    redirect(URL('static', '403.html'))
if block.FORBID_TO is not None:
    if block.FORBID_TO > datetime.datetime.now():
        redirect(URL('static', '403.html'))

dictionaries = bak_and_mag.get_dictionaries()
m_country = dictionaries['country']
identity_document = dictionaries['identity_document']
settlement_type = dictionaries['settlement_type']
house_type = dictionaries['house_type']
diplomas_and_levels = dictionaries['diplomas_and_levels']
vuz_name = dictionaries['vuz_name']
courses = dictionaries['courses']
languages = dictionaries['languages']
achievements = dictionaries['bak_achievements']
rector_rank = dictionaries['rector_rank']
rector_name = dictionaries['rector_name']
educations_form = dictionaries['educations_form']
faculties = dictionaries['faculties']
budget_countries_list = dictionaries['budget_countries_list']
budget_countries_list_without_rf = dictionaries['budget_countries_list_without_rf']
examinations = [['abit_disc1', 'abit_mark1', 'abit_registration1', 'ege_year1'],
                ['abit_disc2', 'abit_mark2', 'abit_registration2', 'ege_year2'],
                ['abit_disc3', 'abit_mark3', 'abit_registration3', 'ege_year3'],
                ['abit_disc4', 'abit_mark4', 'abit_registration4', 'ege_year4'],
                ['abit_disc5', 'abit_mark5', 'abit_registration5', 'ege_year5'],
                ['abit_disc6', 'abit_mark6', 'abit_registration6', 'ege_year6']]
ege_disciplines = db(db.t_disciplines.EXAMINATION_CATEGORY == 1).select(
    db.t_disciplines.id, db.t_disciplines.NAME, db.t_disciplines.MIN_SCORE, cache=(cache.ram, 60 * 60 * 24),
    cacheable=True)
cg_and_disciplines = db((db.a_competition_groups.FO != 4) & (db.t_levels.LEVEL_GROUP == 1)).select(
    db.a_competition_groups.id, db.t_disciplines.id,
    join=[db.t_directions.on(db.a_competition_groups.DIRECTION == db.t_directions.id),
          db.t_levels.on(db.t_directions.LEVEL == db.t_levels.id),
          db.t_competition_groups_exams.on(db.a_competition_groups.id ==
                                           db.t_competition_groups_exams.COMPETITION_GROUP),
          db.t_disciplines.on(db.t_competition_groups_exams.DISC == db.t_disciplines.id)],
    orderby=db.a_competition_groups.id,
    cache=(cache.ram, 60 * 60 * 24), cacheable=True)
ege_disciplines_dict = {}
for ege_discipline in ege_disciplines:
    ege_disciplines_dict[ege_discipline.id] = (ege_discipline.NAME, ege_discipline.MIN_SCORE)
all_cg = cache.ram('all_bak_cg', lambda: bak_and_mag.get_all_cg(1), time_expire=60 * 60 * 24)
links = ['swed', 'edu', 'select_cg', 'marks', 'docs', 'send_app']


def get_cg_disciplines():
    result = dict()
    for row in cg_and_disciplines:
        if row.a_competition_groups.id in result:
            result[row.a_competition_groups.id].append(row.t_disciplines.id)
        else:
            result[row.a_competition_groups.id] = [row.t_disciplines.id]
    return result


cg_and_disciplines_dict = cache.ram('cg_and_d', lambda: get_cg_disciplines(), time_expire=60 * 60 * 24)


def email_confirmed(fun):
    def decorated():
        confirmed = db_xml((db_xml.abit_validation_codes.A_EMAIL == session.abit_email) & (
                db_xml.abit_validation_codes.CONFIRMED == 1)).select().first()
        if confirmed is None:
            redirect(URL('default', 'index'))
        else:
            return fun()

    return decorated


def email_in_session(fun):
    def decorated():
        # or (session.abit_country is None)
        if session.abit_email is None:
            redirect(URL('default', 'index'))
        else:
            return fun()

    return decorated


def swed_validation(form1):
    if form1.vars.birthdate > form1.vars.doc_date:
        form1.errors.birthdate = T('Check date')
        form1.errors.doc_date = T('Check date')
    if form1.vars.birthdate.year > form1.vars.doc_date.year - 14:
        form1.errors.birthdate = T('Check date')
        form1.errors.doc_date = T('Check date')


@email_confirmed
@email_in_session
def swed():
    form1 = bak_and_mag.create_information_form()
    if form1.process(formname='form1', onvalidation=swed_validation).accepted:
        session.abit_f = form1.vars.f
        session.abit_i = form1.vars.i
        session.abit_o = form1.vars.o
        session.abit_country = form1.vars.country
        session.abit_phone = form1.vars.phone
        session.abit_doc_type = form1.vars.doc_type
        session.abit_doc_type_name = identity_document[int(form1.vars.doc_type)]
        session.abit_doc_ser = form1.vars.doc_ser
        session.abit_doc_num = form1.vars.doc_num
        session.abit_doc_src = form1.vars.doc_src
        session.abit_doc_date = form1.vars.doc_date
        session.abit_doc_kodp = form1.vars.doc_kodp
        session.abit_doc_index = form1.vars.doc_index
        session.abit_doc_place = form1.vars.birthplace
        session.abit_doc_birthd = form1.vars.birthdate
        session.abit_district = form1.vars.district
        session.abit_settlement_type = form1.vars.settlementtype
        session.abit_s_type = settlement_type[int(form1.vars.settlementtype)]
        session.abit_point = form1.vars.point
        session.abit_house_type = form1.vars.housetype
        session.abit_h_type = house_type[int(form1.vars.housetype)]
        session.abit_street = form1.vars.street
        session.abit_house = form1.vars.house
        session.abit_case = form1.vars.case
        session.abit_flat = form1.vars.flat
        session.abit_region = form1.vars.region
        if request.vars.calc is not None:
            redirect(URL('bak', 'edu', vars=dict(calc=1)))
        else:
            if form1.vars.link_number is None:
                redirect(URL('bak', 'edu'))
            else:
                if form1.vars.link_number == '':
                    redirect(URL('bak', 'edu'))
                else:
                    redirect(URL(links[int(form1.vars.link_number)]))
    return dict(form1=form1)


def swed_in_session(fun):
    def decorated():
        information_list = ['abit_f', 'abit_i', 'abit_country', 'abit_phone', 'abit_doc_type', 'abit_doc_type_name',
                            'abit_doc_num', 'abit_doc_src', 'abit_doc_date', 'abit_doc_index', 'abit_doc_place',
                            'abit_doc_birthd', 'abit_district', 'abit_settlement_type', 'abit_s_type', 'abit_point',
                            'abit_house_type', 'abit_h_type', 'abit_street', 'abit_house', 'abit_case', 'abit_flat',
                            'abit_region']
        for x in information_list:
            if session[x] is None:
                redirect(URL('bak', 'swed', vars=dict(session=x)))
        else:
            return fun()

    return decorated


@swed_in_session
@email_in_session
def edu():
    # Формируем json строку для обработки в JS
    session_level = session.edu_lvl if session.edu_lvl else None
    session_docs_edu = session.edu_docsedu if session.edu_docsedu else None

    educational_info = list()
    entrant_level = dict()
    educational_document = dict()
    level = -1
    for row in diplomas_and_levels:
        if row.t_levels.CODE < 6:
            entrant_level[row.s_document_types_app.OBJ_ID] = row.t_levels.NAME
            educational_document[row.s_document_types_app.DOC_TYPE] = row.s_document_types.NAME
            if not educational_info:
                level = row.s_document_types_app.OBJ_ID
                educational_info.append({'eduLevelId': row.s_document_types_app.OBJ_ID,
                                         'eduLevel': row.t_levels.NAME,
                                         'eduDocument': [{'eduDocID': row.s_document_types_app.DOC_TYPE,
                                                          'eduDoc': row.s_document_types.NAME}]})
            else:
                if level == row.s_document_types_app.OBJ_ID:
                    educational_info[-1]['eduDocument'].append({'eduDocID': row.s_document_types_app.DOC_TYPE,
                                                                'eduDoc': row.s_document_types.NAME})
                else:
                    level = row.s_document_types_app.OBJ_ID
                    educational_info.append({'eduLevelId': row.s_document_types_app.OBJ_ID,
                                             'eduLevel': row.t_levels.NAME,
                                             'eduDocument': [{'eduDocID': row.s_document_types_app.DOC_TYPE,
                                                              'eduDoc': row.s_document_types.NAME}]})
    json_educational_info = json.dumps(educational_info)
    form = bak_and_mag.create_educational_form(entrant_level, 0)
    if form.process(formname='form').accepted:
        session.edu_name = form.vars.name
        session.edu_year = form.vars.year
        session.edu_adr = form.vars.adr
        session.edu_att = form.vars.att
        session.edu_language = form.vars.edu_language
        session.edu_language_name = languages[int(form.vars.edu_language)]
        session.edu_att_date = form.vars.att_date
        session.edu_course = form.vars.course
        session.edu_course_name = courses[int(form.vars.course)]
        session.abit_hostel = form.vars.hostel
        session.abit_army = form.vars.army
        session.edu_lvl = form.vars.lvl
        session.edu_docsedu = form.vars.docsedu
        session.edu_docsedu_name = educational_document[int(form.vars.docsedu)]
        session.edu_region = form.vars.region
        if request.vars.calc is not None:
            redirect(URL('bak', 'docs'))
        else:
            if form.vars.link_number is None:
                redirect(URL('bak', 'select_cg'))
            else:
                if form.vars.link_number == '':
                    redirect(URL('bak', 'select_cg'))
                else:
                    redirect(URL(links[int(form.vars.link_number)]))
    return dict(form=form, json_educational_info=json_educational_info, session_level=session_level,
                session_docs_edu=session_docs_edu)


def edu_in_session(fun):
    def decorated():
        if (session.edu_name is None) or (session.edu_year is None) or (session.edu_adr is None) or \
                (session.edu_att is None) or (session.edu_language is None) or (session.edu_language_name is None) or \
                (session.edu_att_date is None) or (session.edu_course is None) or (session.edu_course_name is None) or \
                (session.edu_lvl is None) or (session.edu_docsedu is None):
            redirect(URL('bak', 'edu'))
        else:
            return fun()
    return decorated


@edu_in_session
@swed_in_session
@email_in_session
def select_cg():
    my_data = cache.ram('bak_cg', lambda: bak_and_mag.create_json(all_cg), time_expire=60 * 60 * 24)

    list_fo = ''
    for row in educations_form:
        list_fo = f'{list_fo}["{row}","{educations_form[row]}"],'
    list_fo = list_fo[0:-1]
    list_fo = f'[{list_fo}]'

    list_fac = ''
    for row in faculties:
        list_fac = f'{list_fac}["{row}","{faculties[row]}"],'
    list_fac = list_fac[0:-1]
    list_fac = f'[{list_fac}]'

    competitions = ''
    if session.prog_list is not None:
        session.prog_list = bak_and_mag.delete_superfluous_cg(session.prog_list, all_cg)
        for a in session.prog_list:
            disc = ''
            # проверяем количество мест если изменился уровень образования
            for cg in all_cg:
                if cg['CG_ID'] == int(a['cg_id']):
                    for d in cg_and_disciplines_dict[int(a["cg_id"])]:
                        disc = f'{disc}["{ege_disciplines_dict[d][0]}","{ege_disciplines_dict[d][1]}"],'
                    disc = disc[0:-1]
                    place = cg['BUDGET_PLACES']
                    if (session.edu_lvl == '3') or (session.edu_lvl == '5') or (session.edu_lvl == '6') or \
                            (int(session.abit_country) not in budget_countries_list):
                        place = '0'
                    disc = f'{{"budPlace":"{place}","disc":[{disc}],"cg":"{str(a["comp_group"])}"}}'
                    competitions = f'{competitions}{{"fo":"{str(a["fo"])}","fac":"{str(a["fac"])}","dir":"' \
                                   f'{str(a["dir"])}","pr":"{str(a["prog"])}","cg":"{str(a["comp_group"])}",' \
                                   f'"discipline":{disc}}},'
                    break
        competitions = competitions[0:-1]
        competitions = f'[{competitions}]'
    form = FORM(DIV(DIV(INPUT(_type='checkbox', _id='only_budget', _name='only_budget',
                              _class='align-self-center form-check-input agreement-chb mt-0',
                              value=session.only_budget, _value=1)),
                    DIV(P('Участвовать только в бюджетных конкурсах', _class='paragraf statement mb-0')),
                    _class='d-inline-flex justify-content-start my-3 px-3 w-100'),
                DIV(DIV(INPUT(_type='submit', _value=T('Next'), _id='btnNext', _style='display:none;',
                              _class='good-btn w-100'), _class='col'), _class='form-group row'))
    if form.process().accepted:
        session.only_budget = form.vars.only_budget
        redirect(URL('bak', 'marks'))
    return dict(my_data=my_data, list_fo=list_fo, list_fac=list_fac, competitions=competitions, form=form)


@edu_in_session
@swed_in_session
@email_in_session
def load_additional_info():
    a = json.loads(request.vars.data)
    educational_fo = a['fo'] if 'fo' in a else None
    faculty = a['fac'] if 'fac' in a else None
    direction = a['direction'] if 'direction' in a else None
    program = a['pr'] if 'pr' in a else None
    if (educational_fo is not None) and (faculty is not None) and (direction is not None) and (program is not None):
        for c_g in all_cg:
            if (educations_form[c_g['FO']] == educational_fo) and (faculties[c_g['FAC']] == faculty) and \
                    (c_g['DIR_NAME'] == direction) and (c_g['PR_NAME'] == program):
                place = c_g['BUDGET_PLACES']
                if (session.edu_lvl == '3') or (session.edu_lvl == '5') or (session.edu_lvl == '6') or \
                        (int(session.abit_country) not in budget_countries_list):
                    place = '0'
                competition_group = c_g['CG_NAME'] if 'CG_NAME' in c_g else ''
                cg_id = c_g['CG_ID'] if 'CG_ID' in c_g else 0
                program_id = c_g['P_ID'] if 'P_ID' in c_g else 0

                disc = ''
                for d in cg_and_disciplines_dict[int(cg_id)]:
                    disc = f'{disc}["{ege_disciplines_dict[d][0]}","{ege_disciplines_dict[d][1]}"],'
                disc = disc[0:-1]
                i = len(session.prog_list) if session.prog_list is not None else 0
                disc = f'{{"budPlace":"{str(place)}","disc":[{disc}],"competitions":"{i}","cg":"{competition_group}"}}'

                selected_directions = list()
                if session.prog_list is None:
                    session.prog_list = list()
                else:
                    for cg in session.prog_list:
                        if cg['dir'] not in selected_directions:
                            selected_directions.append(cg['dir'])
                if (len(selected_directions) < 3) or \
                        ((len(selected_directions) == 3) and (direction in selected_directions)):
                    if (session.edu_lvl != '3') and (session.edu_lvl != '5') and (session.edu_lvl != '6'):
                        session.prog_list.append({'fo': educational_fo, 'fac': faculty, 'dir': direction,
                                                  'cg_id': cg_id, 'comp_group': competition_group, 'prog': program,
                                                  'prog_id': program_id,
                                                  'bud': 'Да' if place != '0' else 'Нет', 'con': 'Да'})
                    else:
                        session.prog_list.append({'fo': educational_fo, 'fac': faculty, 'dir': direction,
                                                  'cg_id': cg_id, 'comp_group': competition_group, 'prog': program,
                                                  'prog_id': program_id, 'bud': 'Нет', 'con': 'Да'})
                return response.json(disc)


def delete_competition():
    a = json.loads(request.vars.data)
    for i, b in enumerate(session.prog_list):
        if (b['fo'] == a['fo']) & (b['fac'] == a['fac']) & (b['dir'] == a['direction']) & (b['prog'] == a['pr']):
            del session.prog_list[i]
            break


def cg_in_session(fun):
    def decorated():
        if session.prog_list is None:
            redirect(URL('bak', 'select_cg'))
        else:
            if not session.prog_list:
                redirect(URL('bak', 'select_cg'))
            else:
                return fun()

    return decorated


def get_discipline_id_by_name(discipline_name):
    for i in ege_disciplines_dict:
        if ege_disciplines_dict[i][0] == discipline_name:
            return i


def check_marks(form):
    entrant_marks = [[form.vars.disc1, form.vars.mark1, form.vars.registration1, 'mark1'],
                     [form.vars.disc2, form.vars.mark2, form.vars.registration2, 'mark2'],
                     [form.vars.disc3, form.vars.mark3, form.vars.registration3, 'mark3'],
                     [form.vars.disc4, form.vars.mark4, form.vars.registration4, 'mark4'],
                     [form.vars.disc5, form.vars.mark5, form.vars.registration5, 'mark5'],
                     [form.vars.disc6, form.vars.mark6, form.vars.registration6, 'mark6']]
    if form.vars.withoutege is None:
        for i, entrant_value in enumerate(entrant_marks):
            if session[examinations[i][0]] is not None:
                if session[examinations[i][0]] != 'Не задано':
                    if (entrant_value[1] is None) and (entrant_value[2] is None):
                        form.errors[entrant_value[3]] = f'Укажите балл ЕГЭ или запишитесь на внутренние испытания по ' \
                                                        f'дисциплине {session[examinations[i][0]]}'

            if (entrant_value[0] is not None) and (entrant_value[1] is not None):
                if entrant_value[0] != 'Не задано':
                    discipline_id = get_discipline_id_by_name(entrant_value[0])
                    if (entrant_value[1] < ege_disciplines_dict[discipline_id][1]) or (entrant_value[1] > 100):
                        form.errors[entrant_value[3]] = f'Значение должно быть в интервале ' \
                                                        f'[{ege_disciplines_dict[discipline_id][1]}; 100]'

            if (entrant_value[1] is not None) and (entrant_value[2] is not None):
                form.errors[entrant_value[3]] = f'Вы записались на внутренние испытания по дисциплине ' \
                                                f'{session[examinations[i][0]]} и указали для неё балл ЕГЭ - ' \
                                                f'выберите что-то одно'

        if (form.vars.disc4 is not None) and (form.vars.disc4 != 'Не задано') and (form.vars.disc4 == form.vars.disc5):
            form.errors.disc4 = 'Вы выбрали повторяющиеся предметы'
            form.errors.disc5 = 'Вы выбрали повторяющиеся предметы'
    if form.vars.egedocument is not None:
        if form.vars.ege_date is None:
            form.errors.ege_date = 'Заполните дату выдачи'
        if form.vars.ege_date == '':
            form.errors.ege_date = 'Заполните дату выдачи'
        if form.vars.ege_n is None:
            form.errors.ege_n = 'Введите номер'
        if form.vars.ege_n == '':
            form.errors.ege_n = 'Введите номер'
        if form.vars.ege_doc_issued is None:
            form.errors.ege_doc_issued = T('Enter a value')
        if form.vars.ege_doc_issued == '':
            form.errors.ege_doc_issued = T('Enter a value')


@cg_in_session
@edu_in_session
@swed_in_session
@email_in_session
def marks():
    entrant_ege = list()
    ege_years = list(range(request.now.year - 4, request.now.year + 1))
    ege_years.insert(0, '')
    for p in session.prog_list:
        if int(p.get('cg_id')) in cg_and_disciplines_dict:
            for i in cg_and_disciplines_dict[int(p.get('cg_id'))]:
                entrant_ege.append(i)
    entrant_ege = list(set(entrant_ege))

    form_elements = list()

    def get_registration_element(idx):
        if (session.edu_docsedu != '20') or (int(session.abit_country) in budget_countries_list_without_rf):
            return DIV(DIV(INPUT(_type='checkbox', _name=f'registration{idx + 1}', value=session[examinations[idx][2]],
                                 _class='form-check-input agreement-chb my-0', _value=1,
                                 _id=f'registration{idx + 1}'), _class='ege-chb'), _class='col-md-4 mb-3')
        return ''

    for i, ege in enumerate(entrant_ege):
        session[examinations[i][0]] = ege_disciplines_dict[ege][0]
        form_elements.append(
            DIV(DIV(ege_disciplines_dict[ege][0], _class='col-md-4 mb-3'),
                DIV(INPUT(_name=f'mark{i + 1}', _class='form-control input-group-prepend',
                          _value='' if session[examinations[i][1]] is None else session[examinations[i][1]],
                          requires=IS_EMPTY_OR(IS_INT_IN_RANGE(ege_disciplines_dict[ege][1], 101,
                                                               error_message='Введите корректное значение'))),
                    SELECT(*[OPTION(x, _value=x) for x in ege_years], _name=f'ege_year{i + 1}', _class='form-control',
                           _value=session[examinations[i][3]] if session[examinations[i][3]] else '',
                           requires=IS_EMPTY_OR(IS_INT_IN_RANGE(request.now.year - 4, request.now.year + 1))),
                    _class='col-md-4 mb-3 input-group'), get_registration_element(i),
                _class='form-group row text-center'))

    options = [ege_disciplines_dict[k][0] for k in ege_disciplines_dict if k not in entrant_ege]
    options.insert(0, 'Не задано')
    i = len(entrant_ege)
    while i < 6:
        form_elements.append(DIV(
            DIV(SELECT(options, _name=f'disc{i + 1}', _class='form-control',
                       value=session[examinations[i][0]] if session[examinations[i][0]] is not None else 'Не задано',
                       requires=IS_IN_SET(options, zero=T('только одно!'),
                                          error_message='Выберите значения из списка')), _class='col-md-4 mb-3'),
            DIV(INPUT(_name=f'mark{i + 1}', _class='form-control input-group-prepend',
                      _value='' if session[examinations[i][1]] is None else session[examinations[i][1]],
                      requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 101, error_message='Введите корректное значение'))),
                SELECT(*[OPTION(x, _value=x) for x in ege_years], _name=f'ege_year{i + 1}', _class='form-control',
                       _value=session[examinations[i][3]] if session[examinations[i][3]] else '',
                       requires=IS_EMPTY_OR(IS_INT_IN_RANGE(request.now.year - 4, request.now.year + 1))),
                _class='col-md-4 mb-3 input-group'),
            get_registration_element(i), _class='form-group row text-center'))
        i += 1

    if (session.edu_docsedu != '20') or (int(session.abit_country) in budget_countries_list_without_rf):
        header_xml = ('<b class="text-center w-100">Выберите предметы и введите баллы <font color="red">ИЛИ</font>'
                      ' запишитесь на вступительные испытания</b>')
    else:
        header_xml = '<b class="text-center w-100">Выберите предметы и введите баллы</b>'
    form = FORM(
        DIV(DIV(INPUT(_type='checkbox', _name='withoutege', _id='withoutege', _value='1', value=session.withoutege,
                      _class='align-self-center form-check-input agreement-chb mt-0')),
            DIV(P('Не знаю результаты ЕГЭ', _class='paragraf statement mb-0')),
            _class='d-inline-flex justify-content-start my-3 px-3 w-100'),
        DIV(DIV(INPUT(_type='checkbox', _name='egedocument', _id='egedocument', _value='1', value=session.egedocument,
                      _class='align-self-center form-check-input agreement-chb mt-0')),
            DIV(P('Я сдавал(-а) ЕГЭ с другим паспортом', _class='paragraf statement mb-0')),
            _class='d-inline-flex justify-content-start my-3 px-3 w-100'),
        DIV(DIV(LABEL(f'{T("Type of document")}:', _for='ege_doc_type'),
                SELECT(*[OPTION(value_, _value=key_) for key_, value_ in iter(identity_document.items())],
                       _id='ege_doc_type', _name='ege_doc_type', _class='form-control',
                       value=session.ege_doc_type,
                       requires=IS_EMPTY_OR(IS_IN_SET(identity_document.keys(), zero=T('choose one'),
                                                      error_message='Выберите один из'))),
                _class='col-md-4 mb-3'),
            DIV(LABEL(f'{T("Series")}:', _for='ege_s'),
                INPUT(_id='ege_s', _name='ege_s', _class='form-control',
                      _value=session.ege_s), _class='col-md-4 mb-3'),
            DIV(LABEL(f'{T("Number")}:', _for='ege_n'),
                INPUT(_id='ege_n', _name='ege_n', _class='form-control',
                      _value=session.ege_n), _class='col-md-4 mb-3'),
            DIV(LABEL(f'{T("Date of issue")}:', _for='ege_date'),
                INPUT(_type='date', _id='ege_date', _name='ege_date', _class='form-control',
                      _value=session.ege_date, require=IS_EMPTY_OR(IS_DATE())),
                _class='col-md-4 mb-3'),
            DIV(LABEL(f'{T("Division code")}:', _for='ege_code'),
                INPUT(_id='ege_code', _name='ege_code', _class='form-control',
                      _value=session.ege_code), _class='col-md-4 mb-3'),
            DIV(LABEL(f'{T("Is issued")}:', _for='ege_doc_issued'),
                INPUT(_id='ege_doc_issued', _name='ege_doc_issued', _class='form-control',
                      _value=session.ege_doc_issued), _class='col-md-4 mb-3'),
            _id='egeDocRow', _class='form-group row d-none'),
        DIV(DIV(XML(header_xml), _class='col'), _class='form-group row text-center'),
        DIV(
            DIV(B('Название дисциплины'), _class='col-md-4'), DIV(B('Балл ЕГЭ / Год сдачи'), _class='col-md-4'),
            DIV(B('Запись на вступительные испытания'), _class='col-md-4 mb-3') if session.edu_docsedu != '20' else '',
            _class='form-group row mt-3 text-center'),
        *form_elements,
        DIV(DIV(INPUT(_value='Далее', _type='submit', _class='good-btn w-100', _id='next'), _class='col mb-3'),
            _class='form-group row'),
        INPUT(_type='number', _id='link_number', _name='link_number', _class='d-none'))
    if form.process(onvalidation=check_marks).accepted:
        session.abit_mark1 = form.vars.mark1
        session.abit_mark2 = form.vars.mark2
        session.abit_mark3 = form.vars.mark3
        session.abit_mark4 = form.vars.mark4
        session.abit_mark5 = form.vars.mark5
        session.abit_mark6 = form.vars.mark6
        session.abit_registration1 = form.vars.registration1
        session.abit_registration2 = form.vars.registration2
        session.abit_registration3 = form.vars.registration3
        session.abit_registration4 = form.vars.registration4
        session.abit_registration5 = form.vars.registration5
        session.abit_registration6 = form.vars.registration6
        session.ege_year1 = form.vars.ege_year1
        session.ege_year2 = form.vars.ege_year2
        session.ege_year3 = form.vars.ege_year3
        session.ege_year4 = form.vars.ege_year4
        session.ege_year5 = form.vars.ege_year5
        session.ege_year6 = form.vars.ege_year6
        session.withoutege = form.vars.withoutege
        session.egedocument = form.vars.egedocument
        session.ege_doc_type = form.vars.ege_doc_type
        session.ege_s = form.vars.ege_s
        session.ege_n = form.vars.ege_n
        session.ege_date = form.vars.ege_date
        session.ege_doc_issued = form.vars.ege_doc_issued
        session.ege_code = form.vars.ege_code
        if form.vars.link_number is None:
            redirect(URL('bak', 'docs'))
        else:
            if form.vars.link_number == '':
                redirect(URL('bak', 'docs'))
            else:
                redirect(URL(links[int(form.vars.link_number)]))
    return dict(form=form)


def marks_in_session(fun):
    def decorated():
        if ((session.abit_disc1 is None) and (session.without_ege is not None)) or \
                ((session.abit_disc2 is None) and (session.without_ege is not None)) or \
                ((session.abit_mark1 is None) and (session.abit_registration1 is None) and
                 (session.without_ege is not None)) or \
                ((session.abit_mark2 is None) and (session.abit_registration2 is None) and
                 (session.without_ege is not None)):
            redirect(URL('bak', 'marks'))
        else:
            return fun()
    return decorated


def download():
    return response.download(request, db_app)


@marks_in_session
@cg_in_session
@edu_in_session
@swed_in_session
@email_in_session
def docs():
    html_achievements = ''
    for row in achievements:
        html_achievements = f'{html_achievements}<tr><td>{row.NAME}</td><td>{row.SCORES}</td><td>{row.MAX_SCORES}' \
                            f'</td></tr>'
    html_achievements = XML(html_achievements)

    img = db_app(
        db_app.doc_images.person == f'{session.abit_f} {session.abit_i} {session.abit_doc_num} {session.abit_email}'
    ).select(db_app.doc_images.file, db_app.doc_images.doctype, orderby=db_app.doc_images.doctype)

    identity_list, educational_list, achievements_list, other_list, photo, educational_inside_list = \
        list(), list(), list(), list(), list(), list()
    for row in img:
        if row.doctype == 1:
            identity_list.append(row.file)
        elif row.doctype == 2:
            educational_list.append(row.file)
        elif row.doctype == 3:
            achievements_list.append(row.file)
        elif row.doctype == 4:
            other_list.append(row.file)
        elif row.doctype == 20:
            educational_inside_list.append(row.file)
        else:
            photo.append(row.file)

    entrant_identity = bak_and_mag.show_loaded_documents(identity_list, 1)
    entrant_educational = bak_and_mag.show_loaded_documents(educational_list, 2)
    entrant_achievement = bak_and_mag.show_loaded_documents(achievements_list, 3)
    entrant_other = bak_and_mag.show_loaded_documents(other_list, 4)
    entrant_photo = bak_and_mag.show_loaded_documents(photo, 5)
    entrant_educational_inside = bak_and_mag.show_loaded_documents(educational_inside_list, 20)
    form = FORM(DIV(DIV(LABEL(f"{T('Comments')}:", _for='comment'),
                        TEXTAREA(_name='comment', _id='comment', _rows=2, _class='form-control',
                                 _value=session.abit_comment if session.abit_comment is not None else '',
                                 requires=IS_LENGTH(maxsize=1000, error_message='Не более 1000 символов')),
                        _class='col'), _class='form-group row'),
                DIV(DIV(INPUT(_type='submit', _value=T('Next'), _class='good-btn w-100 my-3', _id='btnNext'),
                        _class='col'), _class='form-group row'))
    if form.process().accepted:
        session.abit_comment = form.vars.comment
        redirect(URL('bak', 'send_app'))
    return dict(entrant_identity=entrant_identity, entrant_educational=entrant_educational,
                entrant_achievement=entrant_achievement, entrant_other=entrant_other, entrant_photo=entrant_photo,
                html_achievements=html_achievements, form=form, entrant_educational_inside=entrant_educational_inside)


@marks_in_session
@cg_in_session
@edu_in_session
@swed_in_session
@email_in_session
def load_document():
    return bak_and_mag.load_document(request.vars, session.abit_f, session.abit_i, session.abit_doc_num,
                                     session.abit_email)


def create_application_for_edit(loaded_files):
    competition = ''
    for i, a in enumerate(session.prog_list):
        k = a.get('fo').lower()
        if a.get('bud') == 'Да':
            if a.get('con') == 'Да':
                if session.only_budget is None:
                    osnova = '(бюджет или договорная основа)'
                else:
                    osnova = '(бюджет)'
            else:
                osnova = '(бюджет)'
        else:
            osnova = '(договорная основа)'
        competition = f'{competition}<p class="paragraf statement">{i + 1}. Факультет/институт: <b>{a.get("fac")}' \
                      f'</b>, направление подготовки: <b>{a.get("dir")}</b>, программа обучения: <b>{a.get("prog")}' \
                      f'</b>, форма обучения: <b>{k}</b> {osnova}.</p>'

    subjects = ''
    if session.withoutege is None:
        if (session.abit_mark1 is not None) or (session.abit_mark2 is not None) or (session.abit_mark3 is not None) \
                or (session.abit_mark4 is not None) or (session.abit_mark5 is not None):
            subjects = ('<p class="paragraf statement">Прошу засчитать в качестве результатов вступительных испытаний '
                        'следующее:</p>')

            for i, examination in enumerate(examinations):
                if session[examination[1]] is not None:
                    subjects = f'{subjects}<p class="paragraf statement">{i + 1}. Предмет: <b>' \
                               f'{session[examination[0]]}</b>, количество баллов ЕГЭ: <b>' \
                               f'{session[examination[1]]}</b></p>'
        if not ((session.abit_registration1 is None) and (session.abit_registration2 is None) and
                (session.abit_registration3 is None) and (session.abit_registration4 is None) and
                (session.abit_registration5 is None)):
            subjects = f'{subjects}<p class="paragraf statement">Прошу допустить к сдаче вступительных испытаний, ' \
                       f'проводимых университетом самостоятельно по предмету(-ам):</p>'

            for i, examination in enumerate(examinations):
                if session[examination[2]] is not None:
                    subjects = f'{subjects}<p class="paragraf statement">{i + 1}. <b>{session[examination[0]]}</b></p>'

            subjects = f'{subjects}<p class="paragraf statement">и по их результатам допустить к участию в ' \
                       f'конкурсе.</p>'
    else:
        subjects = '<p class="paragraf statement">Укажу результаты ЕГЭ через личный кабинет абитуриента.</p>'

    army = '<b>Служил(-а)</b> в армии. ' if session.abit_army is not None else ''
    if session.edu_course_name != 'Без курсов':
        courses_xml = f'Закончил(-а) подготовительные курсы {vuz_name}: <b>{session.edu_course_name}</b>. '
    else:
        courses_xml = ''
    if session.abit_hostel is not None:
        hostel = 'Нуждаюсь в общежитии на период обучения.</p>'
    else:
        hostel = 'Не нуждаюсь в общежитии на период обучения.</p>'
    education_xml = f'<p class="paragraf statement">О себе сообщаю: окончил(-а) образовательное учреждение «<b>' \
                    f'{session.edu_name}</b>» расположенное в населённом пункте <b>{session.edu_adr}</b>. ' \
                    f'Подтверждающий документ: <b>{session.edu_docsedu_name}</b>, выдан <b>{session.edu_att_date}' \
                    f'</b>. Серия и номер документа: <b>{session.edu_att}</b>. Год окончания: <b>{session.edu_year}' \
                    f'</b>. {army}Изучал(-а) <b>{session.edu_language_name}</b> язык. {courses_xml}{hostel}'

    address = '{district}{settlementtype} {point}, {housetype} {street}, дом {house}{case}{flat}'.format(
        district=session.abit_district + ' район, ' if session.abit_district else '',
        settlementtype=session.abit_s_type, point=session.abit_point, housetype=session.abit_h_type,
        street=session.abit_street, house=session.abit_house,
        case=', корпус {0}'.format(session.abit_case) if session.abit_case != '' else '',
        flat=', квартира {0}'.format(session.abit_flat) if session.abit_flat != '' else '')
    index = XML(
        'Индекс места жительства <b>{0}</b>. '.format(session.abit_doc_index) if session.abit_flat != '' else '')
    return DIV(DIV(DIV(DIV(_class='col-6'),
                       DIV(P(f'{rector_rank} {vuz_name} {rector_name}', _class='statement'), _class='col-6'),
                       _class='row'),
                   DIV(DIV(P(XML(
                       f'Я, <b>{session.abit_f} {session.abit_i} {session.abit_o}</b>. {session.abit_doc_type_name}:'
                       f' серия - <b>{session.abit_doc_ser}</b>, номер - <b>{session.abit_doc_num}</b>; выдан - '
                       f'<b>{session.abit_doc_src}</b>; дата выдачи <b>{session.abit_doc_date}</b>; код '
                       f'подразделения <b>{session.abit_doc_kodp}</b>; место рождения - <b>{session.abit_doc_place}'
                       f'</b>. Дата рождения <b>{session.abit_doc_birthd}</b>. Гражданство - <b>'
                       f'{m_country[int(session.abit_country)]}</b>. Место жительства - <b>{address}</b>. {index}<br>'
                       f'Телефон(-ы) <b>{session.abit_phone}</b>. E-mail <b>{session.abit_email}</b>.'),
                       _class='paragraf statement st-personal'), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('bak', 'swed'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(H4('ЗАЯВЛЕНИЕ'), _class='col text-center'), _class='row'),
                   DIV(DIV(P('Прошу допустить меня к участию в конкурсе для поступления на:',
                             _class='paragraf statement'), _class='col'), _class='row'),
                   DIV(DIV(XML(competition), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('bak', 'select_cg'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(XML(subjects), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('bak', 'marks'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(XML(education_xml), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('bak', 'edu'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(P(f'Количество прикреплённых файлов: {len(loaded_files)}.', _class='paragraf statement'),
                           _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('bak', 'docs'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'), _class='conteiner'))


def create_xml_entrant(abit_pass):
    E = bak_and_mag.xml_escape

    ege_document = ''
    if session.egedocument is not None:
        ege_document = f'<egeDocument>\n<type>{E(session.ege_doc_type)}</type>\n<series>{E(session.ege_s)}</series>\n' \
                       f'<number>{E(session.ege_n)}</number>\n<date>{E(session.ege_date)}</date>\n<issued>' \
                       f'{E(session.ege_doc_issued)}</issued>\n<code>{E(session.ege_code)}</code>\n</egeDocument>\n'

    str_marks = ''
    for examination in examinations:
        discipline_id = get_discipline_id_by_name(session[examination[0]]) if session[examination[0]] != "" else 0
        ege_year = ''
        if session[examination[3]] is not None:
            if session[examination[3]] != '':
                ege_year = f'<year>{E(session[examination[3]])}</year>\n'
        str_marks = f'{str_marks}\n<exam>\n<name>{E(discipline_id)}</name>\n<mark>' \
                    f'{E(session[examination[1]]) if session[examination[1]] != "" else 0}</mark>\n<reg>' \
                    f'{1 if session[examination[2]] is not None else 0}</reg>\n{ege_year}</exam>'

    programs = ''
    for p in session.prog_list:
        if session.edu_docsedu == '20':
            budget = 1
        else:
            if p.get('bud') == 'Да':
                budget = 1
            else:
                budget = 0
        if p.get('con') == 'Да':
            contract = 1 if session.only_budget is None else 0
        else:
            contract = 0
        # Проверить если человек уже имеет высшее образование то только платка!
        programs = f'{programs}\n<educationalprogram>\n<scheme>{E(p.get("prog_id"))}</scheme>\n<budget>{budget}' \
                   f'</budget>\n<contract>{contract}</contract>\n</educationalprogram>'
    if session.abit_comment is None:
        comment = ''
    else:
        comment = f'<comment>{E(session.abit_comment)}</comment>\n'
    entrant_xml = f'<?xml version="1.0" ?>\n<entrant>\n<personaldata>\n<surname>{E(session.abit_f)}</surname>\n<name>' \
                  f'{E(session.abit_i)}</name>\n<middlename>{E(session.abit_o)}</middlename>\n<phone>' \
                  f'{E(session.abit_phone)}</phone>\n<email>{E(session.abit_email)}</email>\n<identitydoc>' \
                  f'{E(session.abit_doc_type)}</identitydoc>\n<series>{E(session.abit_doc_ser)}</series>\n<number>' \
                  f'{E(session.abit_doc_num)}</number>\n<giveout>{E(session.abit_doc_src)}</giveout>\n<giveoutdate>' \
                  f'{E(session.abit_doc_date)}</giveoutdate>\n<code>{E(session.abit_doc_kodp)}</code>\n<birthplace>' \
                  f'{E(session.abit_doc_place)}</birthplace>\n<birthday>{E(session.abit_doc_birthd)}</birthday>\n' \
                  f'<country>{E(session.abit_country)}</country>\n<index>{E(session.abit_doc_index)}</index>\n' \
                  f'<region>{E(session.abit_region)}</region>\n<district>' \
                  f'{E(session.abit_district) if session.abit_district != "" else ""}</district>\n<settlementtype>' \
                  f'{E(session.abit_settlement_type)}</settlementtype>\n<point>{E(session.abit_point)}</point>\n' \
                  f'<housetype>{E(session.abit_house_type)}</housetype>\n<street>{E(session.abit_street)}</street>\n' \
                  f'<house>{E(session.abit_house)}</house>\n<building>{E(session.abit_case)}</building>\n<flat>' \
                  f'{E(session.abit_flat)}</flat>\n<army>{1 if session.abit_army is not None else 0}</army>\n<hostel>' \
                  f'{1 if session.abit_hostel is not None else 0}</hostel>\n<password>{E(abit_pass)}</password>\n' \
                  f'</personaldata>\n<education>\n<level>{E(session.edu_lvl)}</level>\n<year>{E(session.edu_year)}' \
                  f'</year>\n<name>{E(session.edu_name)}</name>\n<eduRegion>{E(session.edu_region)}</eduRegion>\n' \
                  f'<address>{E(session.edu_adr)}</address>\n<edudoctype>{E(session.edu_docsedu)}</edudoctype>\n' \
                  f'<number>{E(session.edu_att)}</number>\n<date>{E(session.edu_att_date)}</date>\n<language>' \
                  f'{E(session.edu_language)}</language>\n<course>{E(session.edu_course)}</course>\n<achievements>\n' \
                  f'<achievement ID="0"/>\n</achievements>\n{comment}</education>\n<educationalprograms>' \
                  f'{programs}\n</educationalprograms>\n<marks>{str_marks}\n</marks>\n{ege_document}</entrant>'
    return entrant_xml


def send_application(entrant_xml, img):
    if (session.abit_registration1 is None) and (session.abit_registration2 is None) and \
            (session.abit_registration3 is None) and (session.abit_registration4 is None) and \
            (session.abit_registration5 is None):
        by_use = 1
    else:
        by_use = 0

    entrant_id = db_xml.xml_files.insert(F=session.abit_f, I=session.abit_i, O=session.abit_o, IS_IMPORTED=0,
                                         XML_FILE=entrant_xml, BY_USE=by_use, IS_CORRECTION=0)
    db_xml.commit()
    for i in img:
        db_xml.xml_files_links.insert(XML_ID=entrant_id, FILE_NAME=i.file, FILE_TYPE=i.doctype)
        db_xml.commit()
    entrant_letter = '<html>Уважаемый абитуриент, Ваше заявление находится в очереди на обработку.</html>'
    mail.send(session.abit_email, 'Копия заявления', entrant_letter)
    return 'Уважаемый абитуриент, Ваше заявление находится в очереди на обработку.'


@marks_in_session
@cg_in_session
@edu_in_session
@swed_in_session
@email_confirmed
@email_in_session
def send_app():
    img = db_app(db_app.doc_images.person ==
                 f'{session.abit_f} {session.abit_i} {session.abit_doc_num} {session.abit_email}').select()
    identity, educational = False, False
    for row in img:
        if row.doctype == 1:
            identity = True
        elif row.doctype == 2:
            educational = True
    if not (identity and educational):
        redirect(URL('bak', 'docs'))
    statement = create_application_for_edit(img)
    heading = DIV(H4('Отправка заявления'))
    form = bak_and_mag.agreement_form(0, request.now.year)
    if form.process(formname='form').accepted:
        try:
            entrant_xml = create_xml_entrant(form.vars.abit_pass)
            result = send_application(entrant_xml, img)
        except Exception as e:
            form = FORM(P(B('Уважаемый абитуриент, Ваше заявление не удалось отправить оператору.'),
                          _style='color:red;font-size:1.5rem;'),
                        DIV(DIV(f'Ошибка: {e}', _class='col'), _class='row mb-3'))
        else:
            bak_and_mag.clear_session()
            heading = ''
            statement = ''
            form = FORM(
                P(B(XML(result)),
                  P('Просим Вас пройти добровольное краткое ',
                    A(B('анкетирование'), _target="_blank",
                      _href='https://docs.google.com/forms/d/1076wAYosavJGyljoUteLfV5jwZJRcQ8EzsN_WkMrB2w/edit'), '.',
                    _class='paragraf lead'), _style='color:green;font-size:1.5rem;'))
    return dict(heading=heading, form=form, statement=statement)
