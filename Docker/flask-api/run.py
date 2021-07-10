import os

from app import app
from views import AdvertisementView

app.add_url_rule('/advertisements/', view_func=AdvertisementView.as_view('ads_list'),
                 methods=['GET', 'POST'])
app.add_url_rule('/advertisements/<int:ad_id>', view_func=AdvertisementView.as_view('ads_retrieve'),
                 methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.getenv('PORT', default=5000))
    )
