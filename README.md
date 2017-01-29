# baseball-bb-america-players

Imports all players from Baseball America

## Installation

1. Clone this repository, preferably into a fresh virtualenv
2. Install reqs w/ Pip:

```shell
$ pip install -r requirements.txt
```

## Usage

After installing this package's requirements, hop into the `bbam`
project directory

```shell
$ cd bbam
```

...and then run the spider:

```shell
$ scrapy crawl players -o out.json
```

This particular incantation will write all players to a file named
`out.json`.

## Support Baseball America

If you enjoy their database, consider a
[Baseball America](http://www.baseballamerica.com/) subscription.
