from bs4 import BeautifulSoup

from weather.parser_html import html_parser, weather_parser


def test_html_parser():
    html = (
        "<li>"
        '<div class="day-week">Сегодня</div>'
        '<div class="day-temperature">+20</div>'
        "</li>"
    )
    soup = BeautifulSoup(html, "html.parser")
    day_divs = soup.find("li").find_all("div")

    result = html_parser([day_divs])

    assert result == [{"day-week": "Сегодня", "day-temperature": "+20"}]


def test_weather_parser():
    assert weather_parser(["Ясно", "Дождь"]) == ["Ясно", "Дождь"]