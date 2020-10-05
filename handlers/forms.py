from django import forms
from django.utils.safestring import mark_safe
from .models import Handler
from .utils import RESPONSE_FORMAT, METHODS, RESPONSE_CONTENT_TYPES


class HandlerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HandlerForm, self).__init__(*args, **kwargs)
        self.fields['push_support'].required = False
        self.fields['response_structure'].required = False

    aggregator = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>USSD aggregator whose requests will be handled "
                            "by this handler.</pre><br>"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. DMARK"
            }
        ))
    short_code = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>The USSD shortcode provided by the aggregator "
                            "above.</pre><hr>"),
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. 255",
                "class": "form-control"
            }
        ))
    request_format = forms.CharField(
        help_text=mark_safe("<pre  style='font-size:8pt;color:#757575'>The format of the request string from "
                            "aggregator's USSD API e.g.\nin <b>{{from=msisdn}}</b>, the values of key <b>msisdn</b> "
                            "in the request will be converted \nand assigned to key <b>from</b> before being sent to "
                            "RapidPro by the channel.</pre><br>"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. {{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                               "{{text=ussdRequestString}}, {{datetime=creationTime}}"
            }
        ))
    response_format = forms.CharField(
        help_text=mark_safe("<pre  style='font-size:8pt;color:#757575'>Specify whether the response to  aggregator API "
                            "should be json or a string \nthat starts with a keyword. This ensures the right USSD "
                            "Menu is sent to the user</pre>"),
        widget=forms.Select(
            choices=RESPONSE_FORMAT,
            attrs={
                "class": "form-control",
            }
        )
    )
    response_content_type = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>Content type of the response expected by the "
                            "aggregator API</pre>"),
        widget=forms.Select(
            choices=RESPONSE_CONTENT_TYPES,
            attrs={
                "class": "form-control",
            }
        )
    )

    signal_reply_string = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>String keyword that signals when USSD menu "
                            "expects a reply from the user e.g. \n<b>CON</b> for Africa's Talking signals USSD menu "
                            "with reply box.</pre>"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. CON, REQUEST"
            }
        )
    )
    signal_end_string = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>String keyword that signals when user should "
                            "not reply to USSD request e.g. \n<b>END</b> for DMARK means the user will receive a "
                            "non-reply USSD menu.</pre>"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. END"
            }
        )
    )
    response_structure = forms.CharField(
        help_text=mark_safe("<pre id='help-response-structure' style='font-size:8pt;color:#757575'>The structure of the response as expected by "
                            "the aggregator API\n e.g. {{text=responseString}}, {{action=signal}}. means the "
                            "aggregator API expects \na response structure similar to \n"
                            "{\"responseString\":\"Hello User how are you\": \"signal\":\"Signal_keyword\"}</pre><br>"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. {{text=responseString}}, {{action=signal}}",
                "type": "hidden"
            }
        ))
    push_support = forms.BooleanField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>Whether this aggregator API supports USSD PUSH "
                            "protocol (default=unchecked).</pre>")
    )

    response_method = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>Response Method.</pre>"),
        widget=forms.Select(
            choices=METHODS,
            attrs={
                "class": "form-control",
                "value": "POST"
            }
        )
    )

    class Meta:
        model = Handler
        exclude = ["is_active"]
