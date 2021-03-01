from django import forms
from django.utils.safestring import mark_safe
from .models import USSDChannel
import socket

hostname = f"https://{socket.gethostname()}"


class ChannelConfForm(forms.ModelForm):
    send_url = forms.CharField(
        widget=forms.URLInput(
            attrs={
                "placeholder": "Enter Server Domain here",
                "value": f"{hostname}"
            }
        ))
    rapidpro_receive_url = forms.CharField(
        widget=forms.URLInput(
            attrs={
                "placeholder": "Enter Receive URL from RapidPro",
                "value": "https://rapidpro.app/"
            }
        ))
    timeout_after = forms.IntegerField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>Time in seconds the channel should wait for a "
                            "response from RapidPro (default=10s)</pre><br>"),
        widget=forms.NumberInput(
            attrs={
                "value": "10",
            }
        ))
    class Meta:
        model = USSDChannel
        exclude = ["is_active"]
