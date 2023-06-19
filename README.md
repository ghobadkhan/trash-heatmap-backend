<h1>Toronto Trash Heatmap</h1>

<h2>Development</h2>
<h3>Running Flask in Test mode</h3>
<code>flask run --cert="adhoc" --debug</code>
<h3>Using PostgreSQL to handle geospatial data</h3>
PostgreSQL is powerful enough to save and query geospatial data
To enable its power you must install <i>postgis</i> and <i>pgrouting</i> extensions. Follow: 

[Postgis installation](https://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS3UbuntuPGSQLApt)

<h4>Setup database to use postgis<h4>
<b>Never install postgis on the default postgresql db!</b>
You must install it on user's database:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE user_db;

ALTER DATABASE user_db SET search_path=public,postgis,contrib;

\c user_db;

CREATE SCHEMA postgis;

CREATE EXTENSION postgis SCHEMA postgis;
--To check if all went well:
SELECT postgis_full_version();
```
The last line should give you something like this:
```
 POSTGIS="3.2.1" [EXTENSION] PGSQL="140" GEOS="3.10.2-CAPI-1.16.0" PROJ="8.2.1" LIBXML="2.9.13" LIBJSON="0.15" LIBPROTOBUF="1.3.3" WAGYU="0.5.0 (Internal)"
 ```