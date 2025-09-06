from django.http import JsonResponse
from organization.models import Job

def jobs_json(request):
    jobs = Job.objects.all().values('id', 'title', 'company', 'location', 'salary')
    return JsonResponse(list(jobs), safe=False)
