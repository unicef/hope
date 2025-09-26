CREATE EXTENSION IF NOT EXISTS citext;
CREATE COLLATION IF NOT EXISTS "und-ci-det" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);
create or replace function check_unique_document_for_individual(uuid, boolean)
   returns boolean
   language plpgsql
   immutable
  as
$$
begin
    return(select exists(select 1 from household_documenttype where id = $1 and unique_for_individual = $2));
end;
$$
