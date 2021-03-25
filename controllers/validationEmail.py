# -*- coding: utf-8 -*-
import random


def index():
    if (request.vars.bak is None) & (request.vars.mag is None) & (request.vars.asp is None):
        redirect(URL('default', 'index'))
    else:
        if request.vars.calc is not None:
            calculator = INPUT(_value=1, _type='hidden', _name='calc', _id='calc')
        else:
            calculator = INPUT(_value=0, _type='hidden', _name='calc', _id='calc')
        if request.vars.bak is not None:
            btn_value = 1
        elif request.vars.mag is not None:
            btn_value = 2
        else:
            btn_value = 3
        form = FORM(
            DIV(
                P(
                    XML(f"{T('Confirmation code was send to')} <b><a href=\"#\" id=\"link1\" target=\"_blank\"></a>"
                        f"</b><b id=\"nMail\"></b>. {T('If there is no email, check the Spam folder.')}"),
                    _id='msg1', _class='invizible'),
                P(
                    XML(f'{T("Confirmation code was send to your mail")} – <b id="tMail"></b>. '
                        f'{T("If there is no email, check the Spam folder.")}'),
                    _id='msg2', _class='invizible'),
                P(
                    XML(f'{T("Error")}: </p><p id="msg3-2" class="invizible">'
                        f'{T("confirmation code can not be sent to your email")}, '
                        f'{T("try again or connect with us on email")} <b>priem@rgau-msha.ru</b>'),
                    _id='msg3-1', _class='invizible'),
                P(
                    XML(f'{T("Error")}: </p><p id="msg4-2" class="invizible">не удалось записать код подтверждения в '
                        f'БД, {T("try again or connect with us on email")} <b>priem@rgau-msha.ru</b>'),
                    _id='msg4-1', _class='invizible'),
                P(
                    XML(T('Wrong validation code or time is out.')),
                    _id='msg7', _class='error invizible'),
                P(
                    XML(T("Don't use icloud.com, validation code can not be send.")),
                    _id='msg8', _class='error invizible'),
                P(
                    XML(f'Ваше заявление уже принято! Если Вы хотите изменить выбранные ранее направления подготовки '
                        f'воспользуйтесь корректировкой заявления в <a href="https://oas.timacad.ru/webabit">'
                        f'личном кабинете абитуриента</a>.'),
                    _id='msg10', _class='error invizible'),
                P(
                    XML(T(('Your email has already been confirmed. After 5 seconds, You will be redirected to the '
                           'application page.'))),
                    _id='msg11', _class='after-5-sec invizible'),
                _id='target', _class="d-inline-flex text-center evsa"),
            DIV(
                DIV(
                    LABEL('E-mail:', _for='email'),
                    INPUT(_name='email', _id='email', _type='email', _class='form-control', _placeholder='email'),
                    DIV(T('Invalid email address'), _class='invalid-feedback js-validate-ten'),
                    _class='col-md-4 check-email-col-1'),
                DIV(
                    DIV(
                        DIV('{0}:'.format(T('Will be available through')), _class="text-btnCodeLabel"),
                        DIV(_id='timer', _class="text-btnCodeLabel"),
                        DIV(T('seconds'), _class="text-btnCodeLabel"),
                        _id='btnCodeLabel', _class='btnCodeLabel'),
                    INPUT(_type='button', _id='btnCode', _name='send_message', _value=T('Get code'),
                          _class='good-btn btnCode'),
                    _class='col-md-4 check-email-col-2'),
                DIV(
                    LABEL('{0}:'.format(T('Enter code')), _id='inputCodeLabel', _for='code', _class='inputCodeLabel'),
                    INPUT(_type='text', _class='form-control code', _name='code', _id='code',
                          _placeholder=T('Confirmation code'), _disabled='disabled'),
                    _class='col-md-4 check-email-col-3'),
                _class='form-group row validate-email'),
            INPUT(_value=btn_value, _type='hidden', _name='edu_level',
                  _id='edu_level'),
            XML(calculator))
        return dict(form=form)


def VcodeToDbAndMail():
    if request.vars.email is not None:
        email = request.vars.email.strip()
        t = db(db.a_persons.EMAIL == email).select(db.a_persons.id).first()
        if t is None:
            # Проверяем не сгенерирован ли уже код подтверждения за последние 2 мин. или почта уже подтверждена
            cur_time = db_xml.executesql(f"SELECT FIRST 1 SESSION_DATE,CONFIRMED,CURRENT_TIMESTAMP FROM "
                                         f"ABIT_VALIDATION_CODES A WHERE ((A.SESSION_DATE > DATEADD(-2 MINUTE TO "
                                         f"CURRENT_TIMESTAMP))OR(A.CONFIRMED IS NOT NULL)) AND A.A_EMAIL = "
                                         f"'{db_xml._adapter.dialect.quote(email)}' ORDER BY SESSION_DATE DESC")
            if (type(cur_time) == list) and (len(cur_time) == 0):
                valid_code = random.randint(1000000, 9999999)
                code_in_db = True
                try:
                    # записываем в БД почту и код подтверждения
                    db_xml.abit_validation_codes.insert(A_EMAIL=email, V_CODE=valid_code)
                    db_xml.commit()
                except Exception:
                    code_in_db = False
                try:
                    code_in_abit_mail = timacad_mail.send(email, 'Проверочный код',
                                                          'Ваш проверочный код: {0}'.format(valid_code))
                except Exception:
                    code_in_abit_mail = False
                if code_in_db & code_in_abit_mail:
                    domen = email[email.find('@') + 1:]
                    # перенаправление абитуриента на его почтовый сервис
                    rows = db_xml(db_xml.s_email_adress.EMAIL_DOMEN == domen).select(db_xml.s_email_adress.EMAIL_NAME,
                                                                                     db_xml.s_email_adress.EMAIL_LINK)
                    if len(rows) > 0:
                        ajax_answer = '["1","' + rows.first().EMAIL_LINK + '","' + rows.first().EMAIL_NAME + '"]'
                        return ajax_answer
                    else:
                        ajax_answer = '["2"]'
                        return ajax_answer
                else:
                    if code_in_db:
                        ajax_answer = '["3"]'
                        return ajax_answer
                    else:
                        ajax_answer = '["4"]'
                        return ajax_answer
            else:
                if cur_time[0][1] == 1:
                    # здесь отправляем сразу на нужную страницу
                    session.abit_email = email
                    if request.vars.edu_level == '1':
                        ajax_answer = '["11"]'
                        return ajax_answer
                    elif request.vars.edu_level == '2':
                        ajax_answer = '["12"]'
                        return ajax_answer
                    elif request.vars.edu_level == '3':
                        ajax_answer = '["15"]'
                        return ajax_answer
                    else:
                        ajax_answer = '["13"]'
                        return ajax_answer
                else:
                    sec = cur_time[0][2] - cur_time[0][0]
                    sec = 120 - sec.seconds
                    domen = email[email.find('@') + 1:]
                    rows = db_xml(db_xml.s_email_adress.EMAIL_DOMEN == domen).select(db_xml.s_email_adress.EMAIL_NAME,
                                                                                     db_xml.s_email_adress.EMAIL_LINK)
                    if len(rows) > 0:
                        ajax_answer = '["5","' + str(
                            sec) + '","' + rows.first().EMAIL_LINK + '","' + rows.first().EMAIL_NAME + '"]'
                        return ajax_answer
                    else:
                        ajax_answer = '["5","' + str(sec) + '"]'
                        return ajax_answer
        else:
            # Отсылаем в личный кабинет абитуриента
            ajax_answer = '["10"]'
            return ajax_answer


def chekCode():
    if (request.vars.email is not None) and (request.vars.code is not None) and (request.vars.edu_level is not None):
        email = request.vars.email.strip()
        row = db_xml.executesql(f"SELECT * FROM ESP_CHECK_MAIL('{db._adapter.dialect.quote(email)}',"
                                f"{db._adapter.dialect.quote(request.vars.code)})")
        if type(row) == list:
            if len(row) == 0:
                ajax_answer = '["7"]'
                return ajax_answer
            else:
                if type(row[0]) == tuple:
                    if len(row[0]) == 0:
                        ajax_answer = '["7"]'
                        return ajax_answer
                    else:
                        if row[0][0] is None:
                            ajax_answer = '["7"]'
                            return ajax_answer
                        else:
                            if request.vars.edu_level == '1':
                                session.abit_email = email
                                ajax_answer = '["8"]'
                                return ajax_answer
                            elif request.vars.edu_level == '2':
                                session.abit_email = email
                                ajax_answer = '["14"]'
                                return ajax_answer
                            else:
                                ajax_answer = '["13"]'
                                return ajax_answer
                else:
                    ajax_answer = '["7"]'
                    return ajax_answer
        else:
            ajax_answer = '["7"]'
            return ajax_answer
    else:
        ajax_answer = '["13"]'
        return ajax_answer
