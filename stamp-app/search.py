# This is a utility module for with features for preproccessing search results from the Faststamps
# catalog-api before the search results are rendered in HTML.

from typing import List
from pydantic import BaseModel
# import pytest


class StampSearchResults(BaseModel):
    """The results of a stamp search with some calculated attributes with information useful for
       rendering the HTML that represents the search results."""
    query: str
    count: int
    stamps_count: int
    variant_stamps_count: int
    stamps: List[dict]
    search_time: str


class SearchResultPageSpec(BaseModel):
    """A specification of how to construct a search results page with links, given a number of
       search results, a given number of "results per page", a current page of results to present
       based on a `start`search result, and finally a specification of other navigational links
       to other pages with search results."""
    rpp: int
    page_count: int
    current_page: int
    linked_pages: List[int]
    next_page: bool
    previous_page: bool
    first_page: bool
    last_page: bool
    left_ellipsis: bool
    right_ellipsis: bool


def search_result_page_spec(count: int,
                            start: int,
                            rpp: int,
                            linked_pages: int,
                            first_page: bool = False,
                            last_page: bool = False,
                            previous_page: bool = False,
                            next_page: bool = False) -> SearchResultPageSpec:
    """Specification of how to construct a search results page given `count` (number of items /
       search results), `start` (the first item / search result to  display) and `rpp` (the
       number of items / results per page to display)."""
    assert count >= 0
    assert start >= 0
    assert rpp > 0
    assert start % rpp == 0
    assert linked_pages >= 0

    if count == 0:
        result = SearchResultPageSpec(rpp=rpp,
                                      page_count=0,
                                      current_page=0,
                                      linked_pages=[],
                                      next_page=False,
                                      previous_page=False,
                                      first_page=False,
                                      last_page=False,
                                      left_ellipsis=False,
                                      right_ellipsis=False)
    else:
        # Calculate total number of pages
        page_count = (count - 1) // rpp + 1
        # Calculate the current page number
        current_page = start // rpp + 1

        result = SearchResultPageSpec(rpp=rpp,
                                      page_count=page_count,
                                      current_page=current_page,
                                      linked_pages=[],
                                      next_page=next_page,
                                      previous_page=previous_page,
                                      first_page=first_page,
                                      last_page=last_page,
                                      left_ellipsis=False,
                                      right_ellipsis=False)
        first = 0
        last = 0
        if linked_pages >= page_count:
            # All pages will have links
            first = 1
            last = page_count
        elif linked_pages == 0:
            first = 0
            last = -1
        elif linked_pages == 1:
            first = current_page
            last = current_page
        elif linked_pages > 1:
            # Calculate number of pages left and right of current page `n` that will have links. In
            # the case of an even number of linked pages, we link one more page to the left than to
            # the right.
            first = current_page - linked_pages // 2
            last = current_page + linked_pages // 2
            if linked_pages % 2 == 0:
                last -= 1
            # If we've overflowed to the left or right we need to adjust left and right
            if first <= 0:
                last = last + 1 - first
                first = 1
            if last > page_count:
                first = first - (last - page_count)
                last = page_count

        # Build representation with links
        for i in range(first, last+1):
            result.linked_pages.append(i)

        # Check if first page, last page and ellipsis should be shown
        if 1 in result.linked_pages:
            result.first_page = False
        else:
            result.first_page = True
        if page_count in result.linked_pages:
            result.last_page = False
        else:
            result.last_page = True
        if result.linked_pages and result.linked_pages[0] > 1:
            result.left_ellipsis = True
        else:
            result.left_ellipsis = False
        if result.linked_pages and result.linked_pages[-1] < page_count:
            result.right_ellipsis = True
        else:
            result.right_ellipsis = False

    return result


def stamp_search_results(query, response, start, results_per_page) -> StampSearchResults:
    """A StampSearchResults object based on the response from a call to the stamp-catalog
       API, suitable for passing to the HTML rendering function."""
    search_time = float(response.headers["server-timing"].split("=")[1])/1000
    results = response.json()
    # results["stamps"] contains a mixed list of stamps AND stamp variants, so we filter out the
    # proper stamps.
    stamps = [stamp for stamp in results["stamps"] if stamp["id"]["yt_variant"] == '']
    stamps_count = len(stamps)
    result = StampSearchResults(query=query,
                                count=results["count"],
                                stamps_count=stamps_count,
                                variant_stamps_count=results["count"] - stamps_count,
                                stamps=stamps[start:start + results_per_page],
                                search_time=f"{search_time:.3}")
    return result
