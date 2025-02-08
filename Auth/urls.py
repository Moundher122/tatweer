from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login', views.Login.as_view()),
    path('signup', views.Signup.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('update', views.finishthetransporteur.as_view()),
    path('driver', views.adddriver.as_view()),
    path('driver/', views.deletedriver.as_view()),
    path('addproduct', views.addproduct.as_view()),
    path('sort/<int:id>', views.sortie.as_view()),
    path('addfeedback', views.addfeedback.as_view()),
    path('rec', views.RecommendBestTransporterAPIView.as_view()),
    path('road', views.addroad.as_view()),
    path('truck', views.addtruck.as_view()),
    path('truck/<int:id>', views.deletetruck.as_view()),
    path('road/<int:id>', views.deleteroad.as_view()),
    path('<int:id>',views.OptimizeSpace.as_view())
]
