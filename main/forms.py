from django import forms 
from .models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import ProductReview,UserAddressBook

class SignupForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = User
        #django by default only asks for username,pass and email in UserCreationForm
        fields =  UserCreationForm.Meta.fields + ('email','first_name','last_name','password1','password2',)

#Review add form
class ReviewAdd(forms.ModelForm):
	class Meta:
		model=ProductReview
		fields=('review_text','review_rating')

# AddressBook Add Form
class AddressBookForm(forms.ModelForm):
	class Meta:
		model=UserAddressBook
		fields=('pincode','address','mobile','status')

# ProfileEdit
class ProfileForm(UserChangeForm):
	class Meta:
		model=User
		fields=('first_name','last_name','email','username')