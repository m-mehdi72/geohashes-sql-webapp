import pandas as pd
from shapely.geometry import Point, Polygon

def generate_sql_queries(table_name, polygons_info):
    queries = []
    for area_name, polygon_vertices in polygons_info.items():
        if len(polygon_vertices) < 3:
            print("At least three vertices are required to define a polygon.")
            continue

        polygon = Polygon(polygon_vertices)
        min_lat, min_lon, max_lat, max_lon = polygon.bounds

        bounding_box_conditions = [
            f"(t.lat BETWEEN {min_lat} AND {max_lat})",
            f"(t.lon BETWEEN {min_lon} AND {max_lon})"
        ]

        polygon_wkt = "POLYGON(({}))".format(
            ", ".join(f"{lon} {lat}" for lat, lon in polygon_vertices)
        )

        query = f"""
        SELECT *,
        CASE 
            WHEN ST_CONTAINS(ST_GEOGFROMTEXT('{polygon_wkt}'), ST_GEOGPOINT(t.lon, t.lat)) 
            THEN 
                CASE 
                    WHEN '{area_name}' NOT IN 
                        (CASE WHEN 'location' IS NOT NULL THEN 'location' ELSE NULL END)
                    THEN 
                        CASE WHEN 'location' IS NOT NULL THEN CONCAT('{area_name}', ',') ELSE '{area_name}' END
                    ELSE 
                        'location'
                END 
        END AS location
        FROM SQL_EDITOR_{table_name}_TABLE AS t
        WHERE
            {" AND ".join(bounding_box_conditions)}
        """
        queries.append(query)

    final_query = " UNION ALL ".join(queries)
    return final_query

def polygon_query_script(table_name, csv_file):
    df = pd.read_csv(csv_file)

    polygons_info = {}
    for index, row in df.iterrows():
        area_name = row['Name']
        if area_name not in polygons_info:
            polygons_info[area_name] = []
        polygons_info[area_name].append((row['Latitude'], row['Longitude']))

    sql_query = generate_sql_queries(table_name, polygons_info)
    sql_query += ';'
    return sql_query
