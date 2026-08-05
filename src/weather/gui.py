import os
import tkinter as tk
from contextlib import suppress
from tkinter import TclError

from bs4.element import NavigableString
from dotenv import load_dotenv
from requests import RequestException

from .parser_html import find_your_city, parser


class WeatherApp:
    def __init__(self, root, size_x=400, size_y=200):
        self.root = root
        self.size_x = size_x
        self.size_y = size_y
        self.active_tooltip = None
        self.root.title("Погода на неделю")
        self.root.geometry(f"{size_x}x{size_y}")
        self.root.configure(bg="white")

        self.main_container = tk.Frame(
            self.root,
            bg="white",
            highlightthickness=0,
        )
        self.main_container.pack(fill="both", expand=True)

        self.setup_search_section()
        self.setup_weather_grid()

        self.days_data = []
        self.weather_widgets = []
        self.days_temperature = []
        self.api_token = os.getenv("API_TOKEN")

    def setup_search_section(self):
        """Настройка секции поиска с кнопками."""
        search_frame = tk.Frame(
            self.main_container,
            bg="white",
            highlightthickness=0,
        )
        search_frame.pack(fill="x", pady=10, padx=10)

        self.input_entry = tk.Entry(
            search_frame,
            font=("Arial", 10),
            width=30,
            justify="center",
            highlightthickness=0,
            bg="white",
            fg="gray",
        )
        self.input_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        self.input_entry.insert(0, "Поиск по городу...")
        self.input_entry.bind("<FocusIn>", self.on_entry_click)
        self.input_entry.bind("<FocusOut>", self.on_focus_out)

        self.create_buttons(search_frame)

    def create_buttons(self, parent):
        """Централизованное создание кнопок с корректными подсказками."""
        buttons_config = [
            {
                "text": "🔍",
                "command": self.search_city,
                "tooltip": "Поиск города",
            },
            {
                "text": "📍",
                "command": self.get_current_location,
                "tooltip": "Моё местоположение",
            },
            {
                "text": "🔄",
                "command": self.refresh_weather,
                "tooltip": "Обновить погоду",
            },
        ]

        self.buttons = []

        for config in buttons_config:
            btn = tk.Button(
                parent,
                text=config["text"],
                command=config["command"],
                font=("Arial", 10),
                width=3,
                relief="flat",
                bg="#f0f0f0",
                activebackground="#e0e0e0",
            )
            btn.pack(side="left", padx=2)

            self.add_tooltip(btn, config["tooltip"])
            self.buttons.append(btn)

    def add_tooltip(self, widget, text):
        """Добавление всплывающей подсказки с автоматическим скрытием."""
        tooltip_window = None

        def show_tooltip(event):
            nonlocal tooltip_window

            if tooltip_window and tooltip_window.winfo_exists():
                tooltip_window.destroy()
                tooltip_window = None

            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)

            x = event.x_root + 15
            y = event.y_root + 15
            tooltip_window.wm_geometry(f"+{x}+{y}")

            label = tk.Label(
                tooltip_window,
                text=text,
                background="#ffffe0",
                foreground="#000000",
                relief="solid",
                borderwidth=1,
                padx=5,
                pady=2,
                font=("Arial", 9),
            )
            label.pack()

            tooltip_window.after(3000, lambda: hide_tooltip(tooltip_window))

        def hide_tooltip(tooltip_to_hide):
            """Скрыть подсказку."""
            with suppress(TclError):
                if tooltip_to_hide and tooltip_to_hide.winfo_exists():
                    tooltip_to_hide.destroy()

        def on_leave(event):
            """При уходе мыши с виджета - мгновенно скрываем подсказку."""
            nonlocal tooltip_window

            if tooltip_window and tooltip_window.winfo_exists():
                tooltip_window.destroy()
                tooltip_window = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", on_leave)

    def setup_weather_grid(self):
        """Настройка сетки для погодных карточек."""
        self.grid_frame = tk.Frame(
            self.main_container,
            bg="white",
            highlightthickness=0,
        )
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=5)

        for i in range(4):
            self.grid_frame.columnconfigure(i, weight=1)

        for i in range(2):
            self.grid_frame.rowconfigure(i, weight=1)

    def create_weather_cards(self):
        """Создание карточек погоды."""
        colors = [
            "#FFB6C1",
            "#FFDAB9",
            "#E6E6FA",
            "#C1FFC1",
            "#B0E0E6",
            "#F0E68C",
            "#DDA0DD",
        ]

        for widget in self.weather_widgets:
            card = widget.get("card")

            if card is not None:
                with suppress(TclError):
                    card.destroy()

        self.weather_widgets = []

        for i, day in enumerate(self.days_data[:7]):
            row, col = (0, i) if i < 4 else (1, i - 4)

            card = tk.Frame(
                self.grid_frame,
                bg=colors[i],
                relief="groove",
                bd=1,
                highlightthickness=0,
            )
            card.grid(row=row, column=col, padx=3, pady=1, sticky="nsew")

            day_label = tk.Label(
                card,
                text=day,
                font=("Arial", 9, "bold"),
                bg=colors[i],
            )
            day_label.pack(pady=0)

            weather_text = tk.Text(
                card,
                height=3,
                width=10,
                font=("Arial", 8),
                wrap="word",
                bg=colors[i],
                relief="flat",
            )
            weather_text.pack(padx=3, pady=0, fill="both", expand=True)

            self.weather_widgets.append(
                {
                    "card": card,
                    "label": day_label,
                    "text": weather_text,
                    "day": day,
                    "color": colors[i],
                }
            )

    def on_entry_click(self, event):
        if self.input_entry.get() == "Поиск по городу...":
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(fg="black")

    def on_focus_out(self, event):
        if self.input_entry.get() == "":
            self.input_entry.insert(0, "Поиск по городу...")
            self.input_entry.config(fg="gray")

    def search_city(self):
        """Поиск погоды для города."""
        city = self.input_entry.get()

        if city and city != "Поиск по городу...":
            self.input_entry.config(fg="green")
            self.root.after(1500, lambda: self.input_entry.config(fg="gray"))
            self.update_weather(city)

    def get_current_location(self):
        """Получение текущего местоположения."""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, find_your_city(api_token=self.api_token))
        self.input_entry.config(fg="black")
        self.search_city()

    def refresh_weather(self):
        """Обновление погоды."""
        current_city = self.input_entry.get()

        if current_city and current_city != "Поиск по городу...":
            self.update_weather(current_city)

    def order_days(self, days_info):
        """Правильный порядок дней недели."""
        self.days_data = []
        self.days_temperature = []

        for day in days_info:
            self.days_data.append(day["day-week"])

            temperature = day["day-temperature"]

            if isinstance(temperature, NavigableString):
                self.days_temperature.append(str(temperature))
            else:
                self.days_temperature.append(temperature.next)

    def update_weather(self, city):
        """Обновление погоды."""
        try:
            info_days_mas, weather_days_mas = parser(city)

            self.order_days(info_days_mas)
            self.create_weather_cards()

            weather = []

            for i in range(
                min(
                    7,
                    len(self.days_temperature),
                    len(weather_days_mas),
                )
            ):
                weather.append(f"{self.days_temperature[i]}\n{weather_days_mas[i]}")

            for i, widget in enumerate(self.weather_widgets):
                widget["text"].delete(1.0, tk.END)

                if i < len(weather):
                    weather_text = weather[i]
                    widget["text"].insert(1.0, f"{weather_text}")

        except (RequestException, KeyError, IndexError, TclError) as e:
            print(f"Ошибка при обновлении погоды: {e}")


def main():
    load_dotenv()

    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
