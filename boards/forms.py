from django import forms
from django.core.exceptions import ValidationError

from .models import Topic, Post


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )

    def clean_subject(self):
        data = self.cleaned_data["subject"]

        if "test" in data:
            raise ValidationError('Invalid text - string "test" not allowed')

        # Remember to always return the cleaned data.
        return data

    class Meta:
        model = Topic
        fields = ['subject', 'message']


class TopicReplyForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('message',)
