CREATE EXTENSION IF NOT EXISTS citext;
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