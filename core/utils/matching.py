from datetime import date

from matches.models import Block


def calculate_age(date_of_birth):
    if not date_of_birth:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def score_profile_against_preferences(profile, preference):
    if not preference:
        return 0

    checks = []
    age = profile.age

    checks.append((preference.religion, profile.religion))
    checks.append((preference.caste, profile.caste))
    checks.append((preference.mother_tongue, profile.mother_tongue))
    checks.append((preference.country, profile.country))
    checks.append((preference.state, profile.state))
    checks.append((preference.city, profile.city))
    checks.append((preference.education, profile.education))
    checks.append((preference.profession, profile.profession))

    total = 0
    matched = 0

    for preferred, actual in checks:
        if preferred:
            total += 1
            if preferred.lower() == (actual or "").lower():
                matched += 1

    if preference.minimum_age or preference.maximum_age:
        total += 1
        if age is not None:
            min_ok = preference.minimum_age is None or age >= preference.minimum_age
            max_ok = preference.maximum_age is None or age <= preference.maximum_age
            if min_ok and max_ok:
                matched += 1

    if total == 0:
        return 50
    return round((matched / total) * 100, 2)


def get_excluded_user_ids(user):
    blocked_by_user = Block.objects.filter(user=user).values_list("blocked_user_id", flat=True)
    blocked_user = Block.objects.filter(blocked_user=user).values_list("user_id", flat=True)
    return set(blocked_by_user) | set(blocked_user) | {user.id}
