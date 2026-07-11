# Setup and privacy

Enable only the APIs needed in a Google Cloud project and restrict the API key by API and appropriate application constraints.

```sh
export GOOGLE_MAPS_API_KEY='...'
bin/google-maps-query --execute geocode '1600 Amphitheatre Parkway, Mountain View, CA'
bin/google-maps-query --execute reverse 37.422 -122.084
bin/google-maps-query --execute search 'coffee near Union Square'
bin/google-maps-query --execute place PLACE_ID
bin/google-maps-query --execute route 'place_id:ORIGIN_ID' 'place_id:DESTINATION_ID' --mode DRIVE
```

Every command sends query or coordinate data to Google and may be billable. Responses are JSON. The tool does not cache results.

Place IDs are preferred route inputs. Address strings are supported with an `address:` prefix but can be ambiguous. Route modes: `DRIVE`, `BICYCLE`, `WALK`, and `TRANSIT`.

Official references:

- https://developers.google.com/maps/documentation/geocoding
- https://developers.google.com/maps/documentation/places/web-service
- https://developers.google.com/maps/documentation/routes

