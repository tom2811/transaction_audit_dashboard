from allauth.account.forms import LoginForm


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Modern, clean input styling
        input_classes = (
            "block w-full px-4 py-2.5 "
            "text-gray-900 placeholder:text-gray-400 "
            "bg-gray-50 "
            "border border-gray-300 "
            "rounded-lg "
            "focus:outline-none "
            "focus:ring-0 "
            "text-sm"
        )

        self.fields["login"].widget.attrs.update(
            {
                "class": input_classes,
                "placeholder": "Enter your username",
                "autocomplete": "username",
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "class": input_classes,
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )

        self.fields["remember"].widget.attrs.update(
            {
                "class": (
                    "w-4 h-4 "
                    "rounded "
                    "border-gray-300 "
                    "text-gray-900 "
                    "focus:ring-0 "
                    "focus:outline-none "
                    "focus:border-gray-900"
                )
            }
        )
