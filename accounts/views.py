from django.shortcuts import render

from django.contrib.auth.forms import UsernameField
from django import forms
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
import os


valid_cardbacks = ["Cardback", "Space_Marines_Cardback", "Necrons_Cardback", "Chaos_Cardback", "Tyranids_Cardback"]
valid_backgrounds = ["Imperial Aquila"]
if not os.path.exists(os.path.join(os.getcwd(), "user_preferences_storage/")):
    os.mkdir(os.path.join(os.getcwd(), "user_preferences_storage/"))


def change_settings(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            cwd = os.getcwd()
            settings_file = os.path.join(cwd, "user_preferences_storage/" + username + ".txt")
            zoom = str(1.0)
            cardback = request.POST["Cardback"]
            if cardback == "Default":
                cardback = "Cardback"
            else:
                cardback = cardback.replace(" ", "_") + "_Cardback"
            if cardback not in valid_cardbacks:
                cardback = "Cardback"
            else:
                cardback = cardback
            background = request.POST["Background"]
            if background not in valid_backgrounds:
                background = "Imperial Aquila"
            print(cardback)
            print(background)
            full_string = zoom + "\n" + cardback + "\n" + background + "\n"
            with open(settings_file, "w") as f:
                f.write(full_string)
    return redirect("/settings/")


class CustomBaseUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user


class CustomUserCreationForm(CustomBaseUserCreationForm):
    def clean_username(self):
        """Reject usernames that differ only in case."""
        username = self.cleaned_data.get("username")
        if (
            username
            and self._meta.model.objects.filter(username__iexact=username).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "username": self.instance.unique_error_message(
                            self._meta.model, ["username"]
                        )
                    }
                )
            )
        elif not username.isalnum():
            self._update_errors(
                ValidationError(
                    {
                        "username": "Cannot include non-alphanumeric characters"
                    }
                )
            )
        else:
            return username


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
