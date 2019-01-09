# qgs_parser
Parse QGIS project file and create JSON config file

Start the script using `./parse.sh [file.qgs]`, for example, `./parse.sh poum.qgs`

Creates a JSON configuration file called `[file.qgs.json]` in the same directory.

A typical output for a layer could look like that:

```json
  {
    "visible": true,
    "fields": [],
    "mapproxy": "ctbb_poum_layer__tm_limit_pol",
    "indentifiable": false,
    "name": "@ tm_limit_pol",
    "actions": [],
    "hidden": true,
    "type": "layer",
    "showlegend": true
  },
```

Special characters used as layer/group names in QGIS:

* `@` sets `"hidden": true`: Don't show layer/group in layerswitcher (but layer/groups are by default rendered).
* `~` sets `"showlegend": false`: Don't show legend for layer/group.