from django.shortcuts import render


def map_view(request):
	return render(
		request,
		"ingest/map.html",
		{
			"page_title": "Catastro GIS",
			"center_lat": 40.816,
			"center_lng": -4.682,
			"zoom": 11,
		},
	)
