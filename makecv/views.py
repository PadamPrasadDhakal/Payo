from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from .models import User  # replace with your actual model

def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        link = request.POST.get("link")
        git = request.POST.get("git")
        obj = request.POST.get("obj")
        edu = request.POST.get("edu")
        exp = request.POST.get("exp")
        skills = request.POST.get("skills")
        image = request.FILES.get("imge")
        choise = request.POST.get("choise")  # selected template

        # Save to DB
        user_obj = User.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            link=link,
            git=git,
            obj=obj,
            edu=edu,
            exp=exp,
            skills=skills,
            imge=image,
        )

        # Redirect based on template choice
        if choise == "demo1":
            return redirect("makecv:demo1", user_id=user_obj.id)
        elif choise == "demo2":
            return redirect("makecv:demo2", user_id=user_obj.id)
        elif choise == "demo3":
            return redirect("makecv:demo3", user_id=user_obj.id)
        elif choise == "demo4":
            return redirect("makecv:demo4", user_id=user_obj.id)
        elif choise == "demo5":
            return redirect("makecv:demo5", user_id=user_obj.id)
        elif choise == "demo6":
            return redirect("makecv:demo6", user_id=user_obj.id)

    return render(request, "homeis.html")


# Dummy demo views (replace with your real templates)
def demo1(request, user_id):
    detail=get_object_or_404(User,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo1.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

def demo2(request,user_id):
    detail=get_object_or_404(User,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo2.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})
 
def demo3(request,user_id):
    detail=get_object_or_404(User,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo3.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

def demo4(request,user_id):
    detail=get_object_or_404(User,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo4.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

def demo5(request,user_id):
    detail=get_object_or_404(User,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo5.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

def demo6(request,user_id):
   
    detail=get_object_or_404(User,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo6.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})
