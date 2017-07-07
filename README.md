# tzsniff
Sniff out the IANA code for a user's timezone

This repo contains python code to generate a decision tree that can
identify a user's time zone by checking the UTC offset against a
very small set of reference dates. (As of 7/7/17, 6 dates are required
in the worst case).

The python script generates a JSON file (2.3KB gzipped) that is
consumed by a simple (229 Byte unminified) function that returns the
user's time zone IANA code (e.g., `America/New_York`) or `null` if it
cannot be determined.

The time-zone sniffing function only depends on
`Date.getTimezoneOffset` which all browsers since IE5 support.

The decision tree generated does not distinguish between timezones
that only differ before 2000 or for intervals shorter than 1
month. These timezone equivalencies can be seen in
`equivalencies.json`.
