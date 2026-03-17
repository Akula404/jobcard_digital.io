from django import forms
from .models import JobCard, TempSubmission

# -----------------------------
# JobCard Form for Operators
# -----------------------------
class JobCardForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = '__all__'  # include everything
        widgets = {
            # Prepopulated / readonly fields (but still submitted)
            'date': forms.DateInput(attrs={'type': 'date', 'readonly': 'true'}),
            'line': forms.Select(attrs={'readonly': 'true'}),  # visually readonly
            'shift': forms.Select(attrs={'readonly': 'true'}),
            'wo_number': forms.TextInput(attrs={'readonly': 'true'}),
            'product_code': forms.TextInput(attrs={'readonly': 'true'}),
            'product_name': forms.TextInput(attrs={'readonly': 'true'}),
            'target_quantity': forms.NumberInput(attrs={'readonly': 'true'}),

            # Hourly output
            'hour1': forms.NumberInput(), 'hour2': forms.NumberInput(), 'hour3': forms.NumberInput(),
            'hour4': forms.NumberInput(), 'hour5': forms.NumberInput(), 'hour6': forms.NumberInput(),
            'hour7': forms.NumberInput(), 'hour8': forms.NumberInput(), 'hour9': forms.NumberInput(),
            'hour10': forms.NumberInput(), 'hour11': forms.NumberInput(), 'hour12': forms.NumberInput(),

            # Damages
            'jar': forms.NumberInput(), 'cap': forms.NumberInput(), 'front_label': forms.NumberInput(),
            'back_label': forms.NumberInput(), 'carton': forms.NumberInput(), 'sleeve': forms.NumberInput(),
            'sticker': forms.NumberInput(), 'tube': forms.NumberInput(), 'packets': forms.NumberInput(),
            'roll_on_ball': forms.NumberInput(), 'jar_pump': forms.NumberInput(),

            # Personnel
            'operator_names': forms.Textarea(attrs={'rows': 2}),
            'supervisor_names': forms.Textarea(attrs={'rows': 2}),
            'line_captain_signature': forms.TextInput(),
            'supervisor_signature': forms.TextInput(),
        }

# -----------------------------
# TempSubmission Form (unchanged)
# -----------------------------
class TempSubmissionForm(forms.ModelForm):
    class Meta:
        model = TempSubmission
        fields = [
            "hour1","hour2","hour3","hour4","hour5",
            "hour6","hour7","hour8","hour9","hour10","hour11", "hour12"
        ]

# -----------------------------
# JobCard Prepopulate Form (Supervisor)
# -----------------------------
class JobCardPrepopulateForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = [
            "line",
            "shift",
            "wo_number",
            "product_code",
            "product_name",
            "target_quantity",
            "operator_names",
            "supervisor_names",
        ]
        widgets = {
            'line': forms.Select(),
            'shift': forms.Select(),
            'operator_names': forms.Textarea(attrs={'rows': 2}),
            'supervisor_names': forms.Textarea(attrs={'rows': 2}),
        }
