from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User as CVUser  # CV model
from users.models import User  # Main user model
from django.core.files.base import ContentFile
from io import BytesIO
import base64

@login_required
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
        save_to_profile = request.POST.get("save_to_profile")  # checkbox value

        # Save to makecv DB
        cv_user_obj = CVUser.objects.create(
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

        # If user wants to save to profile, update their main user profile
        if save_to_profile == "yes" and request.user.is_authenticated:
            try:
                user = request.user
                # Update user profile fields (always update, not just if empty)
                user.phone = phone[:10] if phone else user.phone or ""
                user.address = address[:255] if address else user.address or ""
                
                # Always update profile photo if provided
                if image:
                    user.profile_photo = image
                
                # Update CV-related fields
                if skills:
                    user.skills = skills
                if edu:
                    user.education_qualification = edu[:100] if edu else user.education_qualification or ""
                if exp:
                    user.experience = exp
                
                # Save the uploaded image as resume file (replacing existing)
                # This saves the CV template data as the resume
                if image:
                    # Use the same image file as resume placeholder
                    # In production, you'd generate a PDF here
                    user.resume = image
                
                user.save()
                messages.success(request, "✅ CV has been saved to your profile and resume file updated!")
            except Exception as e:
                messages.error(request, f"❌ Error saving to profile: {str(e)}")

        # Redirect based on template choice
        if choise == "demo1":
            return redirect("makecv:demo1", user_id=cv_user_obj.id)
        elif choise == "demo2":
            return redirect("makecv:demo2", user_id=cv_user_obj.id)
        elif choise == "demo3":
            return redirect("makecv:demo3", user_id=cv_user_obj.id)
        elif choise == "demo4":
            return redirect("makecv:demo4", user_id=cv_user_obj.id)
        elif choise == "demo5":
            return redirect("makecv:demo5", user_id=cv_user_obj.id)
        elif choise == "demo6":
            return redirect("makecv:demo6", user_id=cv_user_obj.id)

    return render(request, "homeis.html")


# Dummy demo views (replace with your real templates)
@login_required
def demo1(request, user_id):
    detail=get_object_or_404(CVUser,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo1.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

@login_required
def demo2(request,user_id):
    detail=get_object_or_404(CVUser,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo2.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})
 
@login_required
def demo3(request,user_id):
    detail=get_object_or_404(CVUser,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo3.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

@login_required
def demo4(request,user_id):
    detail=get_object_or_404(CVUser,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo4.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

@login_required
def demo5(request,user_id):
    detail=get_object_or_404(CVUser,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo5.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})

@login_required
def demo6(request,user_id):
   
    detail=get_object_or_404(CVUser,id=user_id)
    mylan=detail.git.split(",")
    myskills=detail.skills.split(",")
    myexperience=detail.exp.split(",")
    myeducation=detail.edu.split(",")


    return render(request,"demo6.html",{'detail':detail,'mylan':mylan,'myskills':myskills,'myexperience':myexperience,'myeducation':myeducation})
