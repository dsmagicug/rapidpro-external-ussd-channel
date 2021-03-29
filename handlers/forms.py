from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import Handler
from channel.models import USSDChannel
from .utils import RESPONSE_FORMAT, METHODS, RESPONSE_CONTENT_TYPES, AUTH_SCHEMES


class HandlerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HandlerForm, self).__init__(*args, **kwargs)
        self.fields['push_support'].required = False
        self.fields['response_structure'].required = False
        self.fields['push_url'].required = False
        self.fields['repeat_trigger'].required = False

    aggregator = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>USSD aggregator whose requests will be handled "
                            "by this handler.</pre><br>"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. DMARK"
            }
        ))
    channel = forms.ModelChoiceField(
        help_text=mark_safe(
            "<pre style='font-size:8pt;color:#757575'>Select an already configured channel that this handler will "
            "forward traffic to</pre><br>"),
        queryset=USSDChannel.objects.all().order_by("channel_name"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    short_code = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>The USSD shortcode returned by the aggregator "
                            "in the response string.If aggregator does<br>not return one in the response, please set "
                            "one in settings.DEFAULT_SHORT_CODE</pre><hr>"),
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. 255",
                "class": "form-control",
                "value": settings.DEFAULT_SHORT_CODE
            }
        ))
    repeat_trigger = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>This will be used in flow designs to signal "
                            "when the USSD should repeat a step, <br>Leave blank to use the default \" \". Please "
                            "refer to docs for more details</pre><hr>"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "value": " "
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
        help_text=mark_safe("<pre id='help-response-structure' style='font-size:8pt;color:#757575'>The structure of "
                            "the response as expected by "
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
    push_url = forms.CharField(
        help_text=mark_safe("<pre id='push-url' style='font-size:8pt;color:#757575'>The URL this channel will call "
                            "for USSD PUSH services.</pre>"),
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "value": f"https://aggregator.app"
            }
        ))
    trigger_word = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>Initial word(statement) to trigger initial flow "
                            "executions in RapidPro</pre>"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "value": "USSD",
            }
        )
    )
    expire_on_inactivity_of = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>Expire all contacts out of their flows, "
                            "when handler is idle for these seconds</pre>"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "value": "300",
            }
        )
    )
    auth_scheme = forms.CharField(
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575' >Choose a scheme to authenticate the "
                            "aggregator's API requests.</pre>"),
        widget=forms.Select(
            choices=AUTH_SCHEMES,
            attrs={
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = Handler
        exclude = ["is_active"]
