from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages


class AspiranteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "login_aspirante"

    def test_func(self):
        user = self.request.user

        return (
            user.is_authenticated
            and user.rol == "ASPIRANTE"
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("login_aspirante")

        messages.error(
            self.request,
            "No tienes permisos para acceder a este apartado."
        )

        return redirect("post_login_redirect")
