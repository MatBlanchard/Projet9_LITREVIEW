from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.conf import settings
from django.db.models import CharField, Value, Q
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
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = get_users_viewable_tickets(request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, 'app/flux.html', context={'posts': posts})


@login_required
def posts(request):
    reviews = get_users_reviews(request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = get_users_tickets(request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, 'app/posts.html', context={'posts': posts})


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
    context = {'user': request.user,
               'form': form
               }
    return render(request, 'app/ticket.html', context=context)


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
def review_existing_ticket(request, ticket_id):
    form = forms.ReviewForm()
    ticket = get_object_or_404(models.Ticket, pk=ticket_id)
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('flux')
    context = {
               'ticket': ticket,
               'form': form
               }
    return render(request, 'app/review_existing_ticket.html', context=context)


@login_required
def subscriptions(request):
    form = forms.FollowForm(current_user=request.user,
                            follows=list(models.UserFollows.objects.filter(user=request.user)
                                         .values_list('followed_user_id', flat=True)))
    if request.method == 'POST':
        form = forms.FollowForm(request.POST, current_user=request.user,
                                follows=list(models.UserFollows.objects.filter(user=request.user)
                                             .values_list('followed_user_id', flat=True)))
        if form.is_valid():
            user_follows = form.save(commit=False)
            user_follows.user = request.user
            user_follows.save()
            return redirect('subscriptions')
    context = {
               'form': form,
               'followers': models.UserFollows.objects.filter(followed_user=request.user),
               'follows': models.UserFollows.objects.filter(user=request.user)
               }
    return render(request, 'app/subscriptions.html', context=context)


@login_required
def unfollow(request, follow_id):
    follow = get_object_or_404(models.UserFollows, pk=follow_id)
    follow.delete()
    return redirect('subscriptions')


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, pk=ticket_id)
    ticket.delete()
    return redirect('posts')


@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, pk=ticket_id)
    if ticket.user != request.user:
        return redirect('posts')
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = forms.TicketForm(instance=ticket)
    context = {'form': form, 'ticket': ticket}
    return render(request, 'app/update_ticket.html', context=context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(models.Review, pk=review_id)
    review.delete()
    return redirect('posts')


@login_required
def update_review(request, review_id):
    review = get_object_or_404(models.Review, pk=review_id)
    if review.user != request.user:
        return redirect('posts')
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = forms.ReviewForm(instance=review)
    context = {'form': form, 'review': review}
    return render(request, 'app/update_review.html', context=context)


def get_users_viewable_tickets(user):
    followed_users = models.UserFollows.objects.filter(user=user).values_list('followed_user_id', flat=True)
    return models.Ticket.objects.filter(Q(user=user) | Q(user__in=followed_users)).exclude(review__isnull=False)


def get_users_tickets(user):
    return models.Ticket.objects.filter(user=user).exclude(review__isnull=False)


def get_users_viewable_reviews(user):
    followed_users = models.UserFollows.objects.filter(user=user).values_list('followed_user_id', flat=True)
    return models.Review.objects.filter(Q(user=user) | Q(user__in=followed_users))


def get_users_reviews(user):
    return models.Review.objects.filter(user=user)
