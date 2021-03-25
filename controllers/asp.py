# -*- coding: utf-8 -*-
import datetime
import json
import bak_and_mag


interval = db().select(db.t_admission_schedule.BEGINNING, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()

date_close_app_form_mag = db((db.t_admission_schedule_stages.FO == 1) &
                             (db.t_admission_schedule_stages.LEVEL_GROUP == 2) &
                             (db.t_admission_schedule_stages.CONTRACT == 0) &
                             (db.t_admission_schedule_stages.NUM == 1) &
                             (db.t_admission_schedule_stages.PREFERENTIAL == 0)).select(
    db.t_admission_schedule_stages.CERT_DATE, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()

block = db(db.a_blocks_by_date.BLOCK_TYPE == 'FORBID_WEB_APP').select(db.a_blocks_by_date.FORBID_TO,
                                                                      cache=(cache.ram, 60 * 5), cacheable=True).first()
if (datetime.datetime.now().date() < interval.BEGINNING) | \
        (datetime.datetime.now().date() > date_close_app_form_mag.CERT_DATE):
    redirect(URL('static', '403.html'))
if block.FORBID_TO is not None:
    if block.FORBID_TO > datetime.datetime.now():
        redirect(URL('static', '403.html'))

dictionaries = bak_and_mag.get_dictionaries()
country = dictionaries['country']
identity_document = dictionaries['identity_document']
settlement_type = dictionaries['settlement_type']
house_type = dictionaries['house_type']
diplomas_and_levels = dictionaries['diplomas_and_levels']
vuz_name = dictionaries['vuz_name']
courses = dictionaries['courses']
languages = dictionaries['languages']
achievements = dictionaries['asp_achievements']
rector_rank = dictionaries['rector_rank']
rector_name = dictionaries['rector_name']
educations_form = dictionaries['educations_form']
faculties = dictionaries['faculties']
budget_countries_list = dictionaries['budget_countries_list']
competition_groups_and_disciplines = db((db.a_competition_groups.FO != 4) & (db.t_levels.LEVEL_GROUP == 3)).select(
    db.a_competition_groups.id, db.t_disciplines.id, db.t_disciplines.MIN_SCORE, db.t_disciplines.NAME,
    db.t_exams_schedule.EXAM_DATE, db.t_exams_schedule.EXAM_TIME,
    join=[db.t_directions.on(db.a_competition_groups.DIRECTION == db.t_directions.id),
          db.t_levels.on(db.t_directions.LEVEL == db.t_levels.id),
          db.t_competition_groups_exams.on(db.a_competition_groups.id ==
                                           db.t_competition_groups_exams.COMPETITION_GROUP),
          db.t_disciplines.on(db.t_competition_groups_exams.DISC == db.t_disciplines.id)],
    left=db.t_exams_schedule.on(db.t_disciplines.id == db.t_exams_schedule.DISC),
    orderby=db.a_competition_groups.id | db.t_exams_schedule.EXAM_DATE | db.t_exams_schedule.EXAM_TIME,
    groupby=(db.a_competition_groups.id | db.t_disciplines.id | db.t_disciplines.NAME | db.t_exams_schedule.EXAM_DATE |
             db.t_exams_schedule.EXAM_TIME | db.t_disciplines.MIN_SCORE),
    cache=(cache.ram, 60 * 60 * 24), cacheable=True)
asp_disciplines = db(db.t_disciplines.EXAMINATION_CATEGORY == 3).select(
    db.t_disciplines.id, db.t_disciplines.NAME, db.t_disciplines.MIN_SCORE, cache=(cache.ram, 60 * 60 * 24),
    cacheable=True)
cg_and_disciplines = db((db.a_competition_groups.FO != 4) & (db.t_levels.LEVEL_GROUP == 3)).select(
    db.a_competition_groups.id, db.t_disciplines.id,
    join=[db.t_directions.on(db.a_competition_groups.DIRECTION == db.t_directions.id),
          db.t_levels.on(db.t_directions.LEVEL == db.t_levels.id),
          db.t_competition_groups_exams.on(db.a_competition_groups.id ==
                                           db.t_competition_groups_exams.COMPETITION_GROUP),
          db.t_disciplines.on(db.t_competition_groups_exams.DISC == db.t_disciplines.id)],
    orderby=db.a_competition_groups.id,
    cache=(cache.ram, 60 * 60 * 24), cacheable=True)
asp_disciplines_dict = {}
for asp_discipline in asp_disciplines:
    asp_disciplines_dict[asp_discipline.id] = (asp_discipline.NAME, asp_discipline.MIN_SCORE)
all_cg = cache.ram('all_asp_cg', lambda: bak_and_mag.get_all_cg(3), time_expire=60 * 60 * 24)
examinations = [('exam_date_1', 'exam_name_1'), ('exam_date_2', 'exam_name_2'), ('exam_date_3', 'exam_name_3'),
                ('exam_date_4', 'exam_name_4'), ('exam_date_5', 'exam_name_5')]
links = ['swed', 'edu', 'select_cg', 'marks', 'docs', 'send_app']


def get_cg_disciplines():
    result = dict()
    for row in cg_and_disciplines:
        if row.a_competition_groups.id in result:
            result[row.a_competition_groups.id].append(row.t_disciplines.id)
        else:
            result[row.a_competition_groups.id] = [row.t_disciplines.id]
    return result


cg_and_disciplines_dict = cache.ram('cg_and_d_asp', lambda: get_cg_disciplines(), time_expire=60 * 60 * 24)


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
        form1.errors.doc_date = T('Wrong date')


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
        if form1.vars.link_number is None:
            redirect(URL('asp', 'edu'))
        else:
            if form1.vars.link_number == '':
                redirect(URL('asp', 'edu'))
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
                redirect(URL('asp', 'swed', vars=dict(session=x)))
        else:
            return fun()

    return decorated


@swed_in_session
@email_in_session
def edu():
    entrant_level = dict()
    for row in diplomas_and_levels:
        if row.t_levels.CODE in (4, 5, 6):
            entrant_level[row.s_document_types_app.OBJ_ID] = row.t_levels.NAME
    form = bak_and_mag.create_educational_form(entrant_level, 1)
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
        session.edu_region = form.vars.region
        session.edu_docsedu = 'Диплом о высшем профессиональном образовании'
        if form.vars.link_number is None:
            redirect(URL('asp', 'select_cg'))
        else:
            if form.vars.link_number == '':
                redirect(URL('asp', 'select_cg'))
            else:
                redirect(URL(links[int(form.vars.link_number)]))
    return dict(form=form, vuzName=vuz_name)


@swed_in_session
def get_edu_swed():
    row = db_stud((db_stud.a_persons.id == db_stud.a_students.PERSON) & (db_stud.a_persons.F == session.abit_f) &
                  (db_stud.a_persons.I == session.abit_i) & (db_stud.a_persons.O == session.abit_o) &
                  (db_stud.a_persons.BIRTHDATE == session.abit_doc_birthd)).select(
        db_stud.a_students.CERT_SER, db_stud.a_students.CERT_NUM, db_stud.a_students.CERT_DATE).last()
    educational_info = dict()
    if row is not None:
        educational_info["abitEduDocNum"] = '{0} {1}'.format(str(row.CERT_SER) if row.CERT_SER is not None else '',
                                                             str(row.CERT_NUM) if row.CERT_NUM is not None else '')
        educational_info["abitEduDocDate"] = str(row.CERT_DATE) if row.CERT_DATE is not None else ''
    return json.dumps(educational_info)


def edu_in_session(fun):
    def decorated():
        if (session.edu_name is None) or (session.edu_year is None) or (session.edu_adr is None) or \
                (session.edu_att is None) or (session.edu_language is None) or (session.edu_language_name is None) or \
                (session.edu_att_date is None) or (session.edu_course is None) or (session.edu_course_name is None) or \
                (session.edu_lvl is None) or (session.edu_docsedu is None):
            redirect(URL('asp', 'edu'))
        else:
            return fun()

    return decorated


@edu_in_session
@swed_in_session
@email_in_session
def select_cg():
    my_data = cache.ram('asp_cg', lambda: bak_and_mag.create_json(all_cg), time_expire=60 * 60 * 24)

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
            for cg in all_cg:
                if cg['CG_ID'] == int(a['cg_id']):
                    for d in cg_and_disciplines_dict[cg['CG_ID']]:
                        disc = f'{disc}["{asp_disciplines_dict[d][0]}","{asp_disciplines_dict[d][1]}"],'
                    disc = disc[0:-1]
                    place = cg['BUDGET_PLACES']
                    if (session.edu_lvl == '7') or (int(session.abit_country) not in budget_countries_list):
                        place = 0
                    disc = f'{{"budPlace":"{place}","disc":[{disc}],"cg":"{str(a["comp_group"])}"}}'
                    competitions = f'{competitions}{{"fo":"{str(a["fo"])}","fac":"{str(a["fac"])}","dir":' \
                                   f'"{str(a["dir"])}","pr":"{str(a["prog"])}","cg":"' \
                                   f'{str(a["comp_group"])}","discipline":{disc}}},'
                    break
        competitions = competitions[0:-1]
        competitions = f'[{competitions}]'
    return dict(my_data=my_data, list_fo=list_fo, list_fac=list_fac, competitions=competitions)


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
                contract_places = c_g['CONTRACT_PLACES']
                if (session.edu_lvl == '7') or (int(session.abit_country) not in budget_countries_list):
                    place = '0'
                competition_group = c_g['CG_NAME'] if 'CG_NAME' in c_g else ''
                cg_id = c_g['CG_ID'] if 'CG_ID' in c_g else 0
                program_id = c_g['P_ID'] if 'P_ID' in c_g else 0

                disc = ''
                for cg in all_cg:
                    if cg['CG_ID'] == cg_id:
                        if cg['CG_ID'] in cg_and_disciplines_dict:
                            for d in cg_and_disciplines_dict[cg['CG_ID']]:
                                disc = f'{disc}["{asp_disciplines_dict[d][0]}","{asp_disciplines_dict[d][1]}"],'
                disc = disc[0:-1]
                i = len(session.prog_list) if session.prog_list is not None else 0
                disc = f'{{"budPlace":"{place}","disc":[{disc}],"competitions":"{i}","cg":"{competition_group}"}}'
                if session.prog_list is None:
                    session.prog_list = list()
                if session.edu_lvl != '7':
                    session.prog_list.append({'fo': educational_fo, 'fac': faculty, 'dir': direction, 'cg_id': cg_id,
                                              'comp_group': competition_group, 'prog': program, 'prog_id': program_id,
                                              'bud': 'Да' if place != '0' else 'Нет',
                                              'con': 'Да' if contract_places > 0 else 'Нет'})
                else:
                    session.prog_list.append({'fo': educational_fo, 'fac': faculty, 'dir': direction, 'cg_id': cg_id,
                                              'comp_group': competition_group, 'prog': program, 'prog_id': program_id,
                                              'bud': 'Нет', 'con': 'Да' if contract_places > 0 else 'Нет'})
                return response.json(disc)


def delete_competition():
    a = json.loads(request.vars.data)
    for i, b in enumerate(session.prog_list):
        if (b['fo'] == a['fo']) and (b['fac'] == a['fac']) and (b['dir'] == a['direction']) and (b['prog'] == a['pr']):
            del session.prog_list[i]
            break


# def check_marks(form):
#    if form.vars.exam_date_1 == form.vars.exam_date_2:
#        form.errors.exam_date_1 = 'Даты не могут совпадать'


def cg_in_session(fun):
    def decorated():
        if session.prog_list is None:
            redirect(URL('asp', 'select_cg'))
        else:
            if not session.prog_list:
                redirect(URL('asp', 'select_cg'))
            else:
                superfluous_cg = list()
                for cg in session.prog_list:
                    for asp_cg in all_cg:
                        if int(cg['cg_id']) == asp_cg['CG_ID']:
                            break
                    else:
                        superfluous_cg.append(cg)
                for x in superfluous_cg:
                    session.prog_list.remove(x)
                if not session.prog_list:
                    redirect(URL('asp', 'select_cg'))
                else:
                    return fun()

    return decorated


"""@cg_in_session
@edu_in_session
@swed_in_session
@email_in_session
def marks():
    competition_groups = set(x.get('cg_id') for x in session.prog_list)

    entrant_cg_and_disciplines = list()
    for group in competition_groups:
        for x in competition_groups_and_disciplines:
            if group == x.a_competition_groups.id:
                entrant_cg_and_disciplines.append(x)

    subject_id = -1
    unique_subjects = dict()
    for subject in entrant_cg_and_disciplines:
        if subject.t_disciplines.id != subject_id:
            subject_id = subject.t_disciplines.id
            if subject_id in unique_subjects:
                if [subject.t_exams_schedule.EXAM_DATE, subject.t_exams_schedule.EXAM_TIME] not in \
                        unique_subjects[subject_id]:
                    unique_subjects[subject_id].append([subject.t_exams_schedule.EXAM_DATE,
                                                        subject.t_exams_schedule.EXAM_TIME])
            else:
                unique_subjects[subject_id] = [[subject.t_exams_schedule.EXAM_DATE, subject.t_exams_schedule.EXAM_TIME]]

    max_cg = {1: session.exam_date_1, 2: session.exam_date_2, 3: session.exam_date_3, 4: session.exam_date_4,
              5: session.exam_date_5}
    tr = list()
    index = 1
    for x in unique_subjects:
        if index < len(max_cg) + 1:
            current_test_datetime = list()
            for y in unique_subjects[x]:
                if (y[0] is not None) and (y[1] is not None):
                    if y[0] > datetime.datetime.now().date():
                        current_test_datetime.append(OPTION(f'{y[0].strftime("%dd.%mm.%YY")} {y[1].strftime("%H:%M")}'))

            tr.append(DIV(DIV(LABEL(asp_disciplines_dict[x][0], _for=f'exam_date_{index}'),
                              SELECT(current_test_datetime, _name=f'exam_date_{index}', _id=f'exam_date_{index}',
                                     value=max_cg[index] if max_cg[index] is not None else '',
                                     _class='form-control'),
                              INPUT(_type='hidden', _name=f'exam_name_{index}', _value=asp_disciplines_dict[x][0]),
                              _class='col'), _class='form-group row'))
            index += 1
        else:
            break

    form = FORM(DIV(DIV(P(f'{T("You need to pass the entrance tests in the subjects")}:', _class='paragraf'),
                        _class='col'), _class='form-group row mb-0'),
                DIV(tr),
                DIV(DIV(INPUT(_type='submit', _value=T('Next'), _class='good-btn my-3 w-100', _id='next'),
                        _class='col'),
                    _class='form-group row'),
                INPUT(_type='number', _id='link_number', _name='link_number', _class='d-none'))
    # if form.process(onvalidation=check_marks).accepted:
    if form.process().accepted:
        session.exam_name_1 = form.vars.exam_name_1
        session.exam_date_1 = form.vars.exam_date_1
        session.exam_name_2 = form.vars.exam_name_2
        session.exam_date_2 = form.vars.exam_date_2
        session.exam_name_3 = form.vars.exam_name_3
        session.exam_date_3 = form.vars.exam_date_3
        session.exam_name_4 = form.vars.exam_name_4
        session.exam_date_4 = form.vars.exam_date_4
        session.exam_name_5 = form.vars.exam_name_5
        session.exam_date_5 = form.vars.exam_date_5
        if form.vars.link_number is None:
            redirect(URL('asp', 'docs'))
        else:
            if form.vars.link_number == '':
                redirect(URL('asp', 'docs'))
            else:
                redirect(URL(links[int(form.vars.link_number)]))
    return dict(form=form)


def marks_in_session(fun):
    def decorated():
        if (session.exam_name_1 is None) or (session.exam_date_1 is None):
            redirect(URL('asp', 'marks'))
        else:
            return fun()

    return decorated"""


def download():
    return response.download(request, db_app)


# @marks_in_session
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
    entrant_educational_inside = bak_and_mag.show_loaded_documents(educational_inside_list, 20)
    entrant_photo = bak_and_mag.show_loaded_documents(photo, 5)
    form = FORM(DIV(DIV(LABEL(f"{T('Comments')}:", _for='comment'),
                        TEXTAREA(_name='comment', _id='comment', _rows=2, _class='form-control',
                                 _value=session.abit_comment if session.abit_comment is not None else '',
                                 requires=IS_LENGTH(maxsize=1000, error_message='Не более 1000 символов')),
                        _class='col'), _class='form-group row'),
                DIV(DIV(INPUT(_type='submit', _value=T('Next'), _class='good-btn w-100 my-3', _id='btnNext'),
                        _class='col'), _class='form-group row'))
    if form.process().accepted:
        session.abit_comment = form.vars.comment
        redirect(URL('asp', 'send_app'))
    return dict(entrant_identity=entrant_identity, entrant_educational=entrant_educational,
                entrant_achievement=entrant_achievement, entrant_other=entrant_other, entrant_photo=entrant_photo,
                html_achievements=html_achievements, form=form, entrant_educational_inside=entrant_educational_inside)


# @marks_in_session
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
                osnova = '(бюджет или договорная основа)'
            else:
                osnova = '(бюджет)'
        else:
            osnova = '(договорная основа)'
        competition = f'{competition}<p class="paragraf statement">{str(i + 1)}. Факультет/институт: <b>' \
                      f'{a.get("fac")}</b>, направление подготовки: <b>{a.get("dir")}</b>, программа обучения: ' \
                      f'<b>{a.get("prog")}</b>, форма обучения: <b>{k}</b> {osnova}.</p>'

    subjects = ''
    for i, examination in enumerate(examinations):
        if session[examination[0]] is not None:
            # if session[examination[0]] != '':
            subjects = f'{subjects}<p class="paragraf statement">{str(i + 1)}. Предмет: <b>{session[examination[1]]}' \
                       f'</b>, дата проведения экзамена: <b>{session[examination[0]]}</b></p>'

    army = '<b>Служил(-а)</b> в армии. ' if session.abit_army is not None else ''

    if session.edu_course_name != 'Без курсов':
        courses_xml = f'Закончил(-а) подготовительные курсы {vuz_name}: <b>{session.edu_course_name}</b>. '
    else:
        courses_xml = ''
    if session.abit_hostel is not None:
        hostel = f'Нуждаюсь в общежитии на период обучения.</p>'
    else:
        hostel = 'Не нуждаюсь в общежитии на период обучения.</p>'
    education_xml = f'<p class="paragraf statement">О себе сообщаю: окончил(-а) образовательное учреждение «<b>' \
                    f'{session.edu_name}</b>» расположенное в населённом пункте <b>{session.edu_adr}</b>. ' \
                    f'Подтверждающий документ: <b>{session.edu_docsedu}</b>, выдан <b>{session.edu_att_date}</b>. ' \
                    f'Серия и номер документа: <b>{session.edu_att}</b>. Год окончания: <b>{session.edu_year}</b>.' \
                    f'<br>{army}Изучал(-а) <b>{session.edu_language_name}</b> язык. {courses_xml}{hostel}'
    address = '{district}{settlementtype} {point}, {housetype} {street}, дом {house}{case}{flat}'.format(
        district=f'{session.abit_district} район, ' if session.abit_district else '',
        settlementtype=session.abit_s_type,
        point=session.abit_point,
        housetype=session.abit_h_type,
        street=session.abit_street,
        house=session.abit_house,
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
                       f'{country[int(session.abit_country)]}</b>. Место жительства - <b>{address}</b>. {index}<br>'
                       f'Телефон(-ы) <b>{session.abit_phone}</b>. E-mail <b>{session.abit_email}</b>.'),
                       _class='paragraf statement st-personal'), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('asp', 'swed'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(H4('ЗАЯВЛЕНИЕ'), _class='col text-center'), _class='row'),
                   DIV(DIV(P('Прошу допустить меня к участию в конкурсе для поступления в аспирантуру на:',
                             _class='paragraf statement'), _class='col'), _class='row'),
                   DIV(DIV(XML(competition), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('asp', 'select_cg'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(P('Прошу допустить меня к вступительным испытаниям:', _class='paragraf statement'),
                           _class='col'),
                       _class='row'),
                   DIV(DIV(XML(subjects), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('asp', 'marks'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(XML(education_xml), _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('asp', 'edu'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   DIV(DIV(P(f'Количество прикреплённых файлов: {len(loaded_files)}.', _class='paragraf statement'),
                           _class='col'), _class='row'),
                   DIV(DIV(
                       A(DIV(XML('<span class="glyphicon glyphicon-pencil"></span><p class="p-btn">Редактировать</p>'),
                             _class='my-btn-conteiner'), _href=URL('asp', 'docs'),
                         _class='good-btn col-sm-12 btn-st-personal hover-none'), _class='col-lg-4 col-12'),
                       _class='row mb-2'),
                   _class='conteiner'))


def create_xml_entrant(abit_pass):
    E = bak_and_mag.xml_escape

    str_marks = ''
    for x in examinations:
        if (session[x[0]] is not None) and (session[x[1]] is not None):
            for row in competition_groups_and_disciplines:
                if row.t_disciplines.NAME == session[x[1]]:
                    str_marks = f'{str_marks}\n<exam>\n<name>{row.t_disciplines.id}</name>\n<date>{E(session[x[0]])}' \
                                f'</date>\n</exam>'
                    break

    programs = ''
    for competition_group in session.prog_list:
        budget = 1 if competition_group.get('bud') == 'Да' else 0
        contract = 1 if competition_group.get('con') == 'Да' else 0
        program_id = E(competition_group.get('prog_id')) if competition_group.get('prog_id') is not None else 0
        programs = f'{programs}\n<educationalprogram>\n<scheme>{program_id}</scheme>\n<budget>{budget}</budget>\n' \
                   f'<contract>{contract}</contract>\n</educationalprogram>'
    if session.abit_comment is None:
        comment = ''
    else:
        comment = f'<comment>{bak_and_mag.xml_escape(session.abit_comment)}</comment>\n'
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
                  f'<address>{E(session.edu_adr)}</address>\n<edudoctype>21</edudoctype>\n<number>' \
                  f'{E(session.edu_att)}</number>\n<date>{E(session.edu_att_date)}</date>\n<language>' \
                  f'{E(session.edu_language)}</language>\n<course>{E(session.edu_course)}</course>\n<achievements>' \
                  f'\n<achievement ID="0"/>\n</achievements>\n{comment}</education>\n<educationalprograms>' \
                  f'{programs}\n</educationalprograms>\n<marks>{str_marks}\n</marks>\n</entrant>'
    return entrant_xml


def send_application(entrant_xml, img):
    entrant_id = db_xml.xml_files.insert(F=session.abit_f, I=session.abit_i, O=session.abit_o, IS_IMPORTED=0,
                                         XML_FILE=entrant_xml, BY_USE=0, IS_CORRECTION=0)
    db_xml.commit()
    for i in img:
        db_xml.xml_files_links.insert(XML_ID=entrant_id, FILE_NAME=i.file, FILE_TYPE=i.doctype)
        db_xml.commit()
    entrant_letter = '<html>Уважаемый абитуриент, Ваше заявление находится в очереди на обработку.</html>'
    mail.send(session.abit_email, 'Подача заявления', entrant_letter)
    # <br>Обработка документов занимает до двух дней. Повторная отправка заявлений увеличивает срок обработки.<br>
    # Если Ваши заявления не обработаны в течение двух дней, свяжитесь с нами по почте priem@rgau-msha.ru
    return 'Уважаемый абитуриент, Ваше заявление находится в очереди на обработку.'


# @marks_in_session
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
        redirect(URL('asp', 'docs'))
    statement = create_application_for_edit(img)
    heading = DIV(H4('Отправка заявления'))
    form = bak_and_mag.agreement_form(2, request.now.year)
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
