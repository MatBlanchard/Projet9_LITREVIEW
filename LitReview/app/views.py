from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.conf import settings
from django.db.models import CharField, Value
from . import forms, models
from itertools import chain


class LoginPageView(View):
    template_name = 'app/login.html'
    form_class = forms.LoginForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('flux')
        message = 'Identifiant ou mot de passe invalide.'
        return render(request, self.template_name, context={'form': form, 'message': message})


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'app/signup.html', context={'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def flux(request):
    reviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
            chain(reviews, tickets),
            key=lambda post: post.time_created,
            reverse=True
    )
    return render(request, 'app/flux.html', context={'posts': posts})


@login_required
def posts(request):
    return render(request, 'app/posts.html')


@login_required
def subscriptions(request):
    return render(request, 'app/subscriptions.html')


@login_required
def ticket_form(request):
    form = forms.TicketForm()
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('flux')
    return render(request, 'app/ticket.html', context={'form': form})


@login_required
def review_form(request):
    ticket_form = forms.TicketForm()
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('flux')
    context = {
        'ticket_form': ticket_form,
        'review_form': review_form
    }
    return render(request, 'app/review.html', context=context)


@login_required
def subscriptions(request):
    form = forms.FollowForm()
    if request.method == 'POST':
        form = forms.FollowForm(request.POST)
        if form.is_valid():
            user_follows = form.save(commit=False)
            user_follows.user = request.user
            user_follows.save()
            return redirect('subscriptions')
    context = {'form': form,
               'followers': models.UserFollows.objects.filter(followed_user=request.user),
               'followed': models.UserFollows.objects.filter(user=request.user)
               }
    return render(request, 'app/subscriptions.html', context=context)


def get_users_viewable_tickets(user):
    return models.Ticket.objects.filter(user=user)


def get_users_viewable_reviews(user):
    return models.Review.objects.filter(user=user)
