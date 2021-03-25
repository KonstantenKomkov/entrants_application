# -*- coding: utf-8 -*-
import datetime


def index():
    interval = db().select(db.t_admission_schedule.BEGINNING, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()
    date_close_app_form_bak = db(
        (db.t_admission_schedule_stages.FO == 1) &
        (db.t_admission_schedule_stages.LEVEL_GROUP == 1) &
        (db.t_admission_schedule_stages.CONTRACT == 0) &
        (db.t_admission_schedule_stages.NUM == 2) &
        (db.t_admission_schedule_stages.PREFERENTIAL == 0)
    ).select(db.t_admission_schedule_stages.CERT_DATE, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()
    date_close_app_form_mag = db(
        (db.t_admission_schedule_stages.FO == 1) &
        (db.t_admission_schedule_stages.LEVEL_GROUP == 2) &
        (db.t_admission_schedule_stages.CONTRACT == 0) &
        (db.t_admission_schedule_stages.NUM == 1) &
        (db.t_admission_schedule_stages.PREFERENTIAL == 0)
    ).select(db.t_admission_schedule_stages.CERT_DATE, cache=(cache.ram, 60 * 60 * 24), cacheable=True).first()
    if date_close_app_form_mag.CERT_DATE > date_close_app_form_bak.CERT_DATE:
        date_close_app_form = date_close_app_form_mag.CERT_DATE
    else:
        date_close_app_form = date_close_app_form_bak.CERT_DATE

    # правильно ↓
    if (datetime.datetime.now().date() >= interval.BEGINNING) & \
            (datetime.datetime.now().date() <= date_close_app_form):
        block = db(db.a_blocks_by_date.BLOCK_TYPE == 'FORBID_WEB_APP').select(db.a_blocks_by_date.FORBID_TO,
                                                                              cache=(cache.ram, 60 * 5),
                                                                              cacheable=True).first()

        def get_button_bak():
            if datetime.datetime.now().date() <= date_close_app_form_bak.CERT_DATE:
                btn_name = T("Application to Bachelor's Degree or Specialty")
                bak_btn = DIV(
                    FORM(
                        BUTTON(
                            XML(f'<svg class="svg-btn"><use xlink:href="{URL("static", "images/sprite-symbol.svg")}'
                                f'#011-"></use></svg><div class="edu-level-btn-text">{btn_name}</div>'),
                            _value=1, _class="edu-level", _name="bak", _id="bak"),
                        _action=URL('validationEmail', 'index')),
                    _class="col-sm-12 col-lg-6 text-center edu-level-col-first")
                return bak_btn
            else:
                return ''

        def get_button_mag():
            if datetime.datetime.now().date() <= date_close_app_form_mag.CERT_DATE:
                btn_name = T("Application to Master's Degree")
                mag_btn = DIV(
                    FORM(
                        BUTTON(
                            XML(f'<svg class="svg-btn"><use xlink:href="{URL("static", "images/sprite-symbol.svg")}'
                                f'#041-graduated"></use></svg><div class="edu-level-btn-text">{btn_name}</div>'),
                            _value=2, _class="edu-level", _name="mag", _id="mag"),
                        _action=URL('validationEmail', 'index')),
                    _class="col-sm-12 col-lg-6 text-center edu-level-col-second")
                return mag_btn
            else:
                return ''

        def get_button_asp():
            if datetime.datetime.now().date() <= date_close_app_form_mag.CERT_DATE:
                btn_name = T("Application for admission to graduate school")
                asp_btn = DIV(
                    FORM(
                        BUTTON(
                            XML(f'<svg class="svg-btn"><use xlink:href="{URL("static", "images/sprite-symbol.svg")}'
                                f'#043-graduate"></use></svg><div class="edu-level-btn-text">{btn_name}</div>'),
                            _value=3, _class="edu-level", _name="asp", _id="asp"),
                        _action=URL('validationEmail', 'index')),
                    _class="col-sm-12 col-lg-6 text-center edu-level-col-second")
                return asp_btn
            else:
                return ''

        if block.FORBID_TO is None:
            buttons = DIV(DIV(XML(get_button_bak()), XML(get_button_mag()), XML(get_button_asp()),
                              _class="form-group row edu-level-row justify-content-center"),
                          _class="container-fluid edu-level-form")
        else:
            if block.FORBID_TO < datetime.datetime.now():
                buttons = DIV(DIV(XML(get_button_bak()), XML(get_button_mag()), XML(get_button_asp()),
                                  _class="form-group row edu-level-row justify-content-center"),
                              _class="container-fluid edu-level-form")
            else:
                buttons = DIV(
                    DIV(
                        P(
                            f'Подача заявлений приостановлена до {block.FORBID_TO.strftime("%d.%m.%Y %H:%M:%S")}, в '
                            f'связи, с большой очередью необработанных заявлений.',
                            _class="paragraf statement error",
                            _style="margin-bottom:0;"), _class="col"), _class="row")

        text = DIV(
            DIV(
                H1('Электронная подача документов на поступление'),
                _class="multicontent"),
            P('Прием документов  производится в следующей  последовательности:'),
            P('1.	Подача заявления с выбором желаемых направлений подготовки/специальностей  и приложением сканов '
              'или фотографией  документов, необходимых для поступления (паспорт, аттестат/диплом  и другие согласно '
              'Правил приема).', _class='paragraf'),
            P('2.	Если в загруженной информации допущены ошибки, сотрудники приемной комиссии укажут на них в '
              'ответном сообщении на Вашу электронную почту.', _class='paragraf'),
            P('3.	После обработки поданных заявлений на сайте приемной комиссии в разделе «Оперативная информация» '
              'публикуются списки подавших документы.', _class='paragraf'),
            P('4.	После появления данных поступающего в списке подавших документы появится доступ к личному кабинету '
              'абитуриента. Для входа используйте Вашу почту и пароль, указанный Вами при подаче заявления.',
              _class='paragraf'),
            P(XML('5.	В личном кабинете поступающий может:'
              '<br>– проверить правильность введенных данных, если обнаружена ошибка, о ней нужно сообщить в приемную '
              'комиссию по электронной почте priem@rgau-msha.ru;'
              '<br>–	внести информацию о ЕГЭ (до проверки результатов ЕГЭ по федеральной информационной системе ГИА и '
              'приема);'
              '<br>–	скорректировать ранее выбранные направления подготовки/специальности;'
              '<br>–	подать/отозвать заявление о согласии на зачисление.'), _class='paragraf'),
            P('6. Абитуриентам,  сдающим вступительные испытания, проводимые вузом самостоятельно, необходимо '
              'периодически проверять личный кабинет: в разделе «Вступительные испытания» автоматически '
              'появляется информация о датах и времени проведения вступительных испытаний.', _class='paragraf'),
            XML(f'<div class="row mb-3"><div class="col text-center">'
                f'<video width="400" height="300" poster="{URL("static", "images/ps.png")}" controls '
                f'class="text-center">'
                f'<source src="{URL("static", "video/instruction.webm")}" type="video/webm">'
                f'<source src="{URL("static", "video/instruction.mp4")}" type="video/mp4"></video></div></div>'),
            DIV(P('Уважаемые абитуриенты! Убедительная просьба указывать актуальный номер телефона. Это необходимо для '
                  'оперативной связи с вами.', _class='lead'), _class='jumbotron py-4 mb-3'),
            XML(buttons))
        seconds = 0
        return dict(text=text, seconds=seconds)
    else:
        text = DIV(
            XML('<h4 class="text-center" style="text-transform:uppercase">До старта приёмной кампании осталось:</h4>'))
        # показываем дни до старта приёмной кампании и после её конца (на одной базе)
        if datetime.datetime.now().date() < date_close_app_form:
            delta = datetime.datetime(interval.BEGINNING.year, interval.BEGINNING.month, interval.BEGINNING.day, 0,
                                      0) - datetime.datetime.now()
        else:
            # Возможно этот срок не совсем точен, т.к. 20 может быть воскресенье, но он скорректируется при переходе на
            # новую (актуальную) базу
            delta = datetime.datetime(interval.BEGINNING.year + 1, 6, 20, 0, 0) - datetime.datetime.now()
        seconds = delta.total_seconds()
        return dict(text=text, seconds=seconds)
