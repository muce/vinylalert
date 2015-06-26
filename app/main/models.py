from flask import current_app
from datetime import datetime

# useful URLs
# http://www.discogs.com/stats/contributors?start=0
# http://www.discogs.com/sell/release/509020
class MatchMaker():

    def get_wantlist_items(self, me):
        want_list_items = []
        for i in me.wantlist:
            wantlist_obj = {}
            wantlist_obj['id'] = i.release.id or 'fail'
            wantlist_obj['title'] = i.release.title or 'fail'
            wantlist_obj['year'] = i.release.year or 'fail'
            wantlist_obj['status'] = i.release.status or 'fail'
            wantlist_obj['country'] = i.release.country or 'fail'
            wantlist_obj['data_quality'] = i.release.data_quality or 'fail'
            wantlist_obj['genres'] = i.release.genres or 'fail'
            wantlist_obj['labels'] = i.release.labels or 'fail'
            wantlist_obj['companies'] = "companies"  # i.release.companies
            wantlist_obj['artists'] = i.release.artists or 'fail'
            wantlist_obj['notes'] = "notes"  # i.release.notes
            wantlist_obj['format'] = i.release.formats or 'fail'
            wantlist_obj['credits'] = "credits"  # i.release.credits
            wantlist_obj['tracklist'] = "tracklist"  # i.release.tracklist
            want_list_items.append(wantlist_obj)
        return want_list_items

    def __repr__(self):
        return '<MatchMaker %r>' % self.name
