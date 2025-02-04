from contacts_app.models import Contact
from users_app.models import UserProfile
from rest_framework import serializers
from contacts_app.api.serializers import ContactSerializer
from django.contrib.auth.models import User
from utils.validators import validate_no_html
from users_app.dummy_data import test_contacts, test_tasks
from tasks_app.models import *
from django.contrib.auth import authenticate
from tasks_app.api.serializers import *


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        exclude = ['user']


class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, validators=[validate_no_html])
    email = serializers.CharField(
        max_length=100, validators=[validate_no_html])
    phone = serializers.CharField(max_length=15, validators=[validate_no_html])
    color = serializers.CharField(max_length=7, validators=[validate_no_html])
    contacts = ContactSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'email', 'phone', 'color', 'contacts']


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self):
        '''
        Create and return a new user account.
        '''
        user = self.create_user()
        user_profile = self.create_user_profile(user)
        self.add_contacts(user_profile)
        self.add_tasks(user_profile)
        return user

    def create_user(self):
        '''
        Create and return a new user account.
        '''
        password = self.validated_data['password']
        user = User(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        user.set_password(password)
        user.save()
        return user

    def create_user_profile(self, user):
        '''
        Create and return a new user profile.
        '''
        return UserProfile.objects.create(user=user)

    def add_contacts(self, user_profile):
        '''
        Add contacts to the user profile.
        '''
        for contact_data in test_contacts:
            contact = Contact.objects.create(
                name=contact_data['name'],
                email=contact_data['email'],
                phone=contact_data['phone'],
                color=contact_data['color'],
                user=user_profile  
            )
            user_profile.contacts.add(contact)  

    def add_tasks(self, user_profile):
        '''
        Add tasks to the user profile.
        '''
        for task_data in test_tasks:
            task = self.create_task(task_data, user_profile)
            if task:
                self.add_subtasks(task, task_data.get('subtasks', []))
                self.add_assigned_contacts(task, task_data.get('assigned', []))
                user_profile.tasks.add(task)

    def create_task(self, task_data, user_profile):
        '''
        Create and return a new task.
        '''
        category, _ = Category.objects.get_or_create(
            name=task_data['category'])
        return Task.objects.create(
            title=task_data['title'],
            description=task_data['description'],
            category=category,
            date=task_data['date'],
            priority=task_data['priority'],
            status=task_data['status'],
            user=user_profile
        )

    def add_subtasks(self, task, subtasks):
        '''
        Add subtasks to the task.
        '''
        for subtask_data in subtasks:
            Subtask.objects.create(
                task=task,
                title=subtask_data['task'],
                checked=subtask_data['checked']
            )

    def add_assigned_contacts(self, task, assigned):
        '''
        Add assigned contacts to the task.
        '''
        for assigned_data in assigned:
            try:
                assigned_contact = Contact.objects.get(name=assigned_data['name'], user=task.user)
            except Contact.DoesNotExist:
                continue

            AssignedContact.objects.create(
                task=task,
                contact=assigned_contact,
                color=assigned_data['color']
            )

class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        '''
        Validate the email and password.
        '''
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Benutzer mit dieser E-Mail existiert nicht.")
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Ungültige Anmeldedaten.")
        else:
            raise serializers.ValidationError(
                "E-Mail und Passwort sind erforderlich.")
        attrs['user'] = user
        return attrs
