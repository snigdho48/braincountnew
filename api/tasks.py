from celery import shared_task

from api.services.cv import UpdateImpressionModelAfterEvery1Hr


@shared_task
def update_impressions_hourly():
    try:
        updater = UpdateImpressionModelAfterEvery1Hr()
        updater.get()
        return "Successfully updated impressions"
    except Exception as e:
        return f"Error updating impressions: {str(e)}" 