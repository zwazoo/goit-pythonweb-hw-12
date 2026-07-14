from datetime import date, timedelta


def get_upcoming_birthdays(contacts: list) -> list:
    today = date.today()
    end_range = today + timedelta(days=7)
    upcoming = []

    for contact in contacts:
        this_year_birthday = contact.birthdate.replace(year=today.year)

        if this_year_birthday < today:
            this_year_birthday = this_year_birthday.replace(year=today.year + 1)

        if today <= this_year_birthday <= end_range:
            congratulation_date = this_year_birthday
            day_of_week = congratulation_date.weekday()

            if day_of_week > 4:
                congratulation_date = congratulation_date + timedelta(
                    days=(7 - day_of_week)
                )

            upcoming.append(
                {
                    "id": contact.id,
                    "name": f"{contact.first_name} {contact.last_name}",
                    "congratulation_date": congratulation_date,
                }
            )

    return upcoming
