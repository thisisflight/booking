import datetime
from typing import Optional


def reconfigure_form_dates(request_method, arrival_date: Optional[str], departure_date: Optional[str]):
    """
    Изменение изначальных данных формы на случай если одна
    из дат отсутствует или дата выезда раньше даты въезда
    """
    if arrival_date:
        arrival_date_ = datetime.datetime.strptime(arrival_date, "%Y-%m-%d")
    if departure_date:
        departure_date_ = datetime.datetime.strptime(departure_date, "%Y-%m-%d")
    if departure_date and arrival_date:
        if arrival_date_ >= departure_date_:
            request_method['departure_date'] = (datetime.datetime
                                                .strftime(arrival_date_ + datetime.timedelta(days=1),
                                                          "%Y-%m-%d"))
            departure_date = request_method.get('departure_date')
    if not arrival_date and departure_date:
        request_method['arrival_date'] = (datetime.datetime
                                          .strftime(departure_date_ - datetime.timedelta(days=1),
                                                    "%Y-%m-%d"))
        arrival_date = request_method.get('arrival_date')
    if not departure_date and arrival_date:
        request_method['departure_date'] = (datetime.datetime
                                            .strftime(arrival_date_ + datetime.timedelta(days=1),
                                                      "%Y-%m-%d"))
        departure_date = request_method.get('departure_date')
    return arrival_date, departure_date
