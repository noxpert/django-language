from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect

oauth = OAuth()

auth0 = oauth.register(
    name="auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)


def login_view(request):
    return auth0.authorize_redirect(request, settings.AUTH0_CALLBACK_URL)


def callback(request):
    token = auth0.authorize_access_token(request)
    userinfo = token.get("userinfo") or auth0.userinfo(token=token)

    user_model = get_user_model()
    auth0_id = userinfo.get("sub")
    email = userinfo.get("email", "")
    name = userinfo.get("name", "")

    user, created = user_model.objects.get_or_create(
        username=auth0_id,
        defaults={
            "email": email,
            "first_name": name.split(" ")[0] if name else "",
            "last_name": " ".join(name.split(" ")[1:]) if name else "",
        },
    )

    if not created:
        updated = False
        if email and user.email != email:
            user.email = email
            updated = True
        if name:
            first, *rest = name.split(" ")
            last = " ".join(rest)
            if user.first_name != first:
                user.first_name = first
                updated = True
            if user.last_name != last:
                user.last_name = last
                updated = True
        if updated:
            user.save()

    admin_emails = {email.strip().lower() for email in settings.AUTH0_ADMIN_EMAILS}
    if email and email.lower() in admin_emails and not user.is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])

    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)

    return redirect(settings.LOGIN_REDIRECT_URL or "/")


def logout_view(request):
    request.session.flush()
    return_to = settings.AUTH0_LOGOUT_URL
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?client_id={settings.AUTH0_CLIENT_ID}&returnTo={return_to}"
    )
