from .models import CompanySetting

def company_settings(request):
    try:
        setting = CompanySetting.objects.first()
        company_name = setting.company_name if setting else "W&SMS"
    except CompanySetting.DoesNotExist:
        company_name = "W&SMS"
    return {'company_name': company_name}

def theme_choice(request):
    try:
        setting = CompanySetting.objects.first()
        theme = setting.theme_choice if setting else 'default'
    except CompanySetting.DoesNotExist:
        theme = 'default'
    return {'theme_choice': theme}
