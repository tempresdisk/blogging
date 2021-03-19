import datetime as dt


def footer_year(request):
    current_year = dt.datetime.today().year
    return {
        'year': current_year,
    }
