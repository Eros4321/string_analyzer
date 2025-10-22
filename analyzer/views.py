from django.shortcuts import render

import hashlib
import re
from collections import Counter
from datetime import datetime, timezone

from django.shortcuts import get_object_or_404
from django.utils import timezone as dj_timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from .models import AnalyzedString
from .serializers import AnalyzeCreateSerializer, AnalyzedStringSerializer

def compute_properties(value: str) -> dict:
    # length (number of characters)
    length = len(value)
    # is_palindrome: case-insensitive (we don't remove spaces/punctuation unless you want to)
    is_palindrome = value.lower() == value.lower()[::-1]
    # unique characters
    unique_characters = len(set(value))
    # word_count: split by any whitespace
    word_count = len(value.split())
    # sha256 hash
    sha256_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
    # character frequency map (counts every character)
    char_freq = dict(Counter(value))
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": char_freq,
    }

class GetSpecificString(APIView):
    """
    GET /strings/{string_value}
    We URL-decode the path and lookup by exact value.
    """
    def get(self, request, string_value):
        # exact match on value field
        obj = get_object_or_404(AnalyzedString, value=string_value)
        return Response(AnalyzedStringSerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, string_value):
        obj = get_object_or_404(AnalyzedString, value=string_value)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StringsListView(APIView):
    """
    Handles both:
      POST /strings        → create & analyze new string
      GET /strings?...     → list with filters
    """

    def _parse_bool(self, v):
        if v.lower() in ("true", "1", "yes", "y"):
            return True
        if v.lower() in ("false", "0", "no", "n"):
            return False
        raise ValueError("invalid boolean")

    def post(self, request):
        serializer = AnalyzeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        value = serializer.validated_data["value"]
        if not isinstance(value, str):
            return Response({"detail": "value must be string"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        props = compute_properties(value)
        sha = props["sha256_hash"]

        if AnalyzedString.objects.filter(id=sha).exists():
            return Response({"detail": "String already exists"}, status=status.HTTP_409_CONFLICT)

        obj = AnalyzedString(id=sha, value=value, properties=props, created_at=dj_timezone.now())
        obj.save()
        return Response(AnalyzedStringSerializer(obj).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        qs = AnalyzedString.objects.all()
        filters_applied = {}

        # is_palindrome
        is_pal = request.query_params.get("is_palindrome")
        if is_pal is not None:
            try:
                parsed = self._parse_bool(is_pal)
            except ValueError:
                return Response({"detail": "is_palindrome must be boolean"}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(properties__is_palindrome=parsed)
            filters_applied["is_palindrome"] = parsed

        # min_length
        min_length = request.query_params.get("min_length")
        if min_length is not None:
            try:
                mi = int(min_length)
            except:
                return Response({"detail": "min_length must be integer"}, status=status.HTTP_400_BAD_REQUEST)
            qs = [o for o in qs if o.properties.get("length", 0) >= mi]
            filters_applied["min_length"] = mi

        # max_length
        max_length = request.query_params.get("max_length")
        if max_length is not None:
            try:
                ma = int(max_length)
            except:
                return Response({"detail": "max_length must be integer"}, status=status.HTTP_400_BAD_REQUEST)
            qs = [o for o in qs if o.properties.get("length", 0) <= ma]
            filters_applied["max_length"] = ma

        # word_count
        wc = request.query_params.get("word_count")
        if wc is not None:
            try:
                wci = int(wc)
            except:
                return Response({"detail": "word_count must be integer"}, status=status.HTTP_400_BAD_REQUEST)
            qs = [o for o in qs if o.properties.get("word_count", 0) == wci]
            filters_applied["word_count"] = wci

        # contains_character
        cc = request.query_params.get("contains_character")
        if cc is not None:
            if len(cc) != 1:
                return Response({"detail": "contains_character must be a single character"}, status=status.HTTP_400_BAD_REQUEST)
            qs = [o for o in qs if cc in o.value]
            filters_applied["contains_character"] = cc

        data = [AnalyzedStringSerializer(o).data for o in qs]
        return Response({"data": data, "count": len(data), "filters_applied": filters_applied}, status=status.HTTP_200_OK)

# Natural language parsing - simple heuristic parser
class NaturalLanguageFilterView(APIView):
    """
    GET /strings/filter-by-natural-language?query=...
    Returns: data, count, interpreted_query
    """

    def _parse_query(self, text: str):
        text = text.lower()
        parsed = {}
        # word_count: if 'single word' or 'one word'
        if re.search(r"\bsingle word\b", text) or re.search(r"\bone word\b", text):
            parsed["word_count"] = 1

        # palindromic case
        if "palindrom" in text or "palindromic" in text or "palindrome" in text:
            parsed["is_palindrome"] = True

        # strings longer than N characters -> min_length = N+1
        m = re.search(r"longer than (\d+)", text)
        if m:
            n = int(m.group(1))
            parsed["min_length"] = n + 1

        # strings longer than or equal to N (phrases)
        m2 = re.search(r"at least (\d+)", text)
        if m2:
            parsed["min_length"] = int(m2.group(1))

        # containing letter X
        m3 = re.search(r"contain(?:ing|s)? the letter ([a-z])", text)
        if m3:
            parsed["contains_character"] = m3.group(1)

        # containing the letter z (other phrasing)
        m4 = re.search(r"strings containing the letter (\w)", text)
        if m4:
            parsed["contains_character"] = m4.group(1)

        # containing the first vowel (heuristic: 'first vowel' -> 'a')
        if "first vowel" in text:
            parsed["contains_character"] = "a"

        # conflict detection example: min_length > max_length (we'll parse max if present)
        m5 = re.search(r"shorter than (\d+)", text)
        if m5:
            parsed["max_length"] = int(m5.group(1)) - 1

        return parsed

    def get(self, request):
        q = request.query_params.get("query")
        if not q:
            return Response({"detail":"query parameter required"}, status=status.HTTP_400_BAD_REQUEST)

        parsed = self._parse_query(q)
        if not parsed:
            return Response({"detail":"Unable to parse natural language query"}, status=status.HTTP_400_BAD_REQUEST)

        # detect conflicting filters
        if "min_length" in parsed and "max_length" in parsed:
            if parsed["min_length"] > parsed["max_length"]:
                return Response({"detail":"Conflicting filters (min_length > max_length)"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # apply filters using the same logic as list endpoint
        qs = AnalyzedString.objects.all()
        # Apply each filter
        if parsed.get("is_palindrome") is True:
            qs = qs.filter(properties__is_palindrome=True)

        if "min_length" in parsed:
            mi = parsed["min_length"]
            qs = [o for o in qs if o.properties.get("length",0) >= mi]
        if "max_length" in parsed:
            ma = parsed["max_length"]
            qs = [o for o in qs if o.properties.get("length",0) <= ma]
        if "word_count" in parsed:
            wc = parsed["word_count"]
            qs = [o for o in qs if o.properties.get("word_count",0) == wc]
        if "contains_character" in parsed:
            cc = parsed["contains_character"]
            qs = [o for o in qs if cc in o.value]

        # unify serialization
        if hasattr(qs, "values"):
            items = qs
        else:
            items = qs

        data = [AnalyzedStringSerializer(o).data for o in items]
        return Response({
            "data": data,
            "count": len(data),
            "interpreted_query": {
                "original": q,
                "parsed_filters": parsed
            }
        }, status=status.HTTP_200_OK)

