from datetime import date, timedelta


def get_upcoming_birthdays(contacts: list) -> list:
    """Return contacts whose birthdays fall within the next 7 days.

    If a birthday lands on a weekend, the congratulation date is shifted
    to the following Monday.

    Args:
        contacts: List of Contact instances with a ``birthdate`` attribute.

    Returns:
        List of dicts with keys ``id``, ``name``, and ``congratulation_date``.
    """
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
