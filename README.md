<h1>Toronto Trash Heatmap</h1>

<h2>Development</h2>
<h3>Running Flask in Test mode</h3>
<code>flask run --cert="adhoc" --debug</code>
<h3>MyPy stubs</h3>
For sqlalchemy

1. <code>pip install -U sqlalchemy-stubs</code>
2. Create ```mypy.ini``` config file if you don't have one
3. Add the following to the config file:

        [mypy]
        plugins = sqlmypy