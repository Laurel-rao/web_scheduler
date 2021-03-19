from django import forms
from.models import Email


# 设置密码字段在admin后台，输入和显示的时候为*
class EmailForm(forms.ModelForm):
       class Meta:
        model = Email
        fields = ('EmailType', 'EmailServer', 'SendEmailAdd', 'SendEmailUser', 'SendEmailPsd', 'ReceiversEmail')
        widgets = {
            'SendEmailPsd': forms.PasswordInput(),
        }
