from django.urls import path
from . import views

app_name = "makecv"

urlpatterns = [
    path("", views.home, name="homeis"),
    path("demo1/<int:user_id>/", views.demo1, name="demo1"),
    path("demo2/<int:user_id>/", views.demo2, name="demo2"),
    path("demo3/<int:user_id>/", views.demo3, name="demo3"),
    path("demo4/<int:user_id>/", views.demo4, name="demo4"),
    path("demo5/<int:user_id>/", views.demo5, name="demo5"),
    path("demo6/<int:user_id>/", views.demo6, name="demo6"),
]

