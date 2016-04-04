--Functions use to search the observatroy for information
--------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION OBS_SEARCH(
  search_term text
)
RETURNS TABLE(description text, name text, aggregate text,source text )  as $$
BEGIN
  RETURN QUERY
  EXECUTE format($string$
              SELECT description,
                name,
                  aggregate,
                  replace(split_part(id,'".', 1),'"', '') source
                  FROM observatory.OBS_column
                  where name ilike '%%%L%%'
                  or description ilike '%%%L%%'
                $string$, search_term, search_term);
  RETURN;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION OBS_Search_Tables(
  search_term text
)
RETURNS TABLE(description text, name text, source text) As $$
BEGIN
  RETURN QUERY
  EXECUTE format($string$
                  SELECT
                    description,
                    id,
                    replace(split_part(id,'".', 1),'"', '') As source
                  FROM
                    observatory.obs_table
                  WHERE
                    id ILIKE '%%%s%%'
                $string$, search_term, search_term);
  RETURN;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION OBS_LIST_DIMENSIONS_FOR_TABLE(table_name text )
RETURNS TABLE(colname text) AS $$
BEGIN
  RETURN QUERY
    EXECUTE format('select colname from observatory.OBS_column_table  where table_id = %L ', table_name);
  RETURN;
END
$$ LANGUAGE plpgsql;

--Fuctions used to describe and search segments
--------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION OBS_DESCRIBE_SEGMENT(segment_name text)
returns TABLE(
  id text,
  name text,
  description text,
  column_names text[],
  column_descriptions text[],
  column_ids text[],
  example_function_call text
)as $$
BEGIN
  RETURN QUERY
  EXECUTE
    format(
      $query$
        SELECT observatory.OBS_tag.id, observatory.OBS_tag.name, observatory.OBS_tag.description,
        array_agg(observatory.OBS_column.name) column_names,
        array_agg(observatory.OBS_column.description) column_descriptions,
        array_agg(observatory.OBS_column.id) column_ids,
        'select OBS_AUGMENT_SEGMENT(the_geom,''' || observatory.OBS_tag.id || ''')' example_function_call
        FROM observatory.OBS_tag, observatory.OBS_column_tag, observatory.OBS_column
        where observatory.OBS_tag.id = observatory.OBS_column_tag.tag_id
        and observatory.OBS_column.id = observatory.OBS_column_tag.column_id
        and observatory.OBS_tag.id ilike '%%%s%%'
        group by observatory.OBS_tag.name, observatory.OBS_tag.description, observatory.OBS_tag.id
      $query$, segment_name);
  RETURN;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION OBS_LIST_AVAILABLE_SEGMENTS()
returns TABLE(
  id text,
  name text,
  description text,
  column_names text[],
  column_descriptions text[],
  column_ids text[],
  example_function_call text
) as $$
BEGIN
  RETURN QUERY
    EXECUTE
      $query$
      SELECT observatory.OBS_tag.id, observatory.OBS_tag.name, observatory.OBS_tag.description,
      array_agg(observatory.OBS_column.name) column_names,
      array_agg(observatory.OBS_column.description) column_descriptions,
      array_agg(observatory.OBS_column.id) column_ids,
      'select OBS_AUGMENT_SEGMENT(the_geom,''' || observatory.OBS_tag.id || ''')' example_function_call
      FROM observatory.OBS_tag, observatory.OBS_column_tag, observatory.OBS_column
      where observatory.OBS_tag.id = observatory.OBS_column_tag.tag_id
      and observatory.OBS_column.id = observatory.OBS_column_tag.column_id
      group by observatory.OBS_tag.name, observatory.OBS_tag.description, observatory.OBS_tag.id
      $query$
  RETURN;
END
$$ LANGUAGE plpgsql;
