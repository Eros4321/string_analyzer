from django.urls import path
from .views import GetSpecificString, StringsListView, NaturalLanguageFilterView

urlpatterns = [
    path("strings", StringsListView.as_view(), name="strings"),  # handles both POST & GET
    path("strings/<path:string_value>", GetSpecificString.as_view(), name="get_string"),
    path("strings/filter-by-natural-language", NaturalLanguageFilterView.as_view(), name="nl_filter"),
]
