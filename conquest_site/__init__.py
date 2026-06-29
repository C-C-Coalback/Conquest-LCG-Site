import sys


def _patch_django_template_basecontext_copy():
    if sys.version_info < (3, 14):
        return
    try:
        from django.template.context import BaseContext
    except Exception:
        return

    def _safe_basecontext_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__ = self.__dict__.copy()
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _safe_basecontext_copy


_patch_django_template_basecontext_copy()