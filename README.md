<h1>Toronto Trash Heatmap</h1>

<h2>Development</h2>
<h3>Running Flask in Test mode</h3>
<code>flask run --cert="adhoc" --debug</code>

*UPDATE: Since I've added socket.io to the server, I no longer use the above code. For now see run.py where I directly invoke flask-socketio's run method*

<h2>The File Structure</h2>

The following shows the main structure. Everything else outside of this structure is temp/unimportant

```
project
│   README.md
│   run.py --> runs the socket.io which in turn runs the entire server 
|   requirements.txt   
|   .gitignore
|   LICENSE
|   pyproject.toml  --> Is needed for now to set up some options related to testing   
│
└───src --> In it's base, contains auxiliary files. e.g:
│   │   utils.py
│   │   ...
│   │
│   └───app --> Contains the core backend files. e.g:
│       │   controller.py
│       │   ...
│   
└───instance --> Temporary(ish) instance related folder which contains .env file, conf file, etc
|   │   .env  --> This the runtime environment file
|   │   conf.py --> To configure the backend on each type of environment (Dev,Test,Prod) it's more convenient to use this file
|   |   ...
│   
└───tests
    │   conftest.py  --> Major test set-up file 
    │   ...
```

<h3>Using PostgreSQL to handle geospatial data</h3>
PostgreSQL is powerful enough to save and query geospatial data
To enable its power you must install <i>postgis</i> and <i>pgrouting</i> extensions. Follow: 

[Postgis installation](https://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS3UbuntuPGSQLApt)

<h4>Setup database to use postgis<h4>
<b>Never install postgis on the default postgresql db!</b>
You must install it on user's database:

```bash
sudo su postgres psql
```

```sql
CREATE DATABASE <user_db>;

ALTER DATABASE <user_db> SET search_path=public,postgis,contrib;

\c <user_db>;

CREATE SCHEMA postgis;

CREATE EXTENSION postgis SCHEMA postgis;
--To check if all went well:
SELECT postgis_full_version();
```
The last line should give you something like this:
```
 POSTGIS="3.2.1" [EXTENSION] PGSQL="140" GEOS="3.10.2-CAPI-1.16.0" PROJ="8.2.1" LIBXML="2.9.13" LIBJSON="0.15" LIBPROTOBUF="1.3.3" WAGYU="0.5.0 (Internal)"
 ```

 <h4>PostGIS Resource</h4>
 Please refer to:

[Introduction of PostGIS](https://postgis.net/workshops/postgis-intro/index.html)

<h3>Using Socket.IO</h3>

I mainly use Socket.IO for sending the api token a goog authenticated client

I use ``Flask-SocketIO`` ([Docs](https://flask-socketio.readthedocs.io/en/latest/index.html)) extension. There are few consideration for using this extension:

- The application setup needs a bit of change as the extension wraps around the normal Flask app setup
- There is no easy solution to test a socketio connection. However I managed to employ a bit hacky solution just to make sure the server runs.
- The extension mainly uses ``eventlet`` to serve the application. However it is recommended to use ``gunicorn`` in the production environment and avoid using the eventlet alone.

<h2>Testing</h2>

We use ``pytest``as the test suite.

<h3>Pytest relative import problem</h3>

There is a problem with pytest, that can't recognize relative the imports i.e. the way the app is structured,
pytest won't find the imports from ``src`` by itself. The solution is to configure it. Thats why I added the following
line to ``pyproject.toml``:

```toml
[tool.pytest.ini_options]
pythonpath = [
  "."
]
```

For more info see [this](https://stackoverflow.com/a/50610630).