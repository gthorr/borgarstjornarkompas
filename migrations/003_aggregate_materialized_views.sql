-- Borgarstjórnar­kompás 2026 — endurskoðun á gagnasamleitni-laginu.
--
-- Skiptum úr SECURITY DEFINER RPC-föllum yfir í MATERIALIZED VIEWS sem hressast
-- af triggera þegar nýtt svar kemur inn. Þetta hreinsar Supabase-linter-viðvaranir
-- (#0028 og #0029) en heldur sömu lifandi-hegðun.
--
-- Keyrðu þetta í SQL Editor.

------------------------------------------------------------------------
-- 1. Eldri SECURITY DEFINER föll burt
------------------------------------------------------------------------
drop function if exists public.get_total_responses();
drop function if exists public.get_top1_counts();
drop function if exists public.get_shoe_x_party();
drop function if exists public.get_pool_x_party();
drop function if exists public.get_archetype_x_party();

------------------------------------------------------------------------
-- 2. Materialized views (cached aggregates, refreshed by trigger)
------------------------------------------------------------------------
drop materialized view if exists public.kompas_total_mv cascade;
create materialized view public.kompas_total_mv as
select count(*)::int as total
from public.kompas_responses
where consented = true;

drop materialized view if exists public.kompas_top1_counts_mv cascade;
create materialized view public.kompas_top1_counts_mv as
select
  top3->0->>'code'        as list_letter,
  top3->0->>'short_name'  as party_name,
  count(*)::int           as n
from public.kompas_responses
where consented = true
  and top3 is not null
  and jsonb_array_length(top3) > 0
group by 1, 2;

drop materialized view if exists public.kompas_shoe_x_party_mv cascade;
create materialized view public.kompas_shoe_x_party_mv as
select
  answers_chaos->>'c01_skostaerd' as shoe_size,
  top3->0->>'code'                 as list_letter,
  top3->0->>'short_name'           as party_name,
  count(*)::int                    as n
from public.kompas_responses
where consented = true
  and answers_chaos ? 'c01_skostaerd'
  and answers_chaos->>'c01_skostaerd' is not null
  and top3 is not null
  and jsonb_array_length(top3) > 0
group by 1, 2, 3;

drop materialized view if exists public.kompas_pool_x_party_mv cascade;
create materialized view public.kompas_pool_x_party_mv as
select
  answers_chaos->>'c02_uppahalds_laug' as laug,
  top3->0->>'code'                      as list_letter,
  top3->0->>'short_name'                as party_name,
  count(*)::int                         as n
from public.kompas_responses
where consented = true
  and answers_chaos ? 'c02_uppahalds_laug'
  and answers_chaos->>'c02_uppahalds_laug' is not null
  and top3 is not null
  and jsonb_array_length(top3) > 0
group by 1, 2, 3;

drop materialized view if exists public.kompas_archetype_x_party_mv cascade;
create materialized view public.kompas_archetype_x_party_mv as
select
  unnest(archetype_ids)   as archetype_id,
  top3->0->>'code'        as list_letter,
  top3->0->>'short_name'  as party_name,
  count(*)::int           as n
from public.kompas_responses
where consented = true
  and archetype_ids is not null
  and array_length(archetype_ids, 1) > 0
  and top3 is not null
  and jsonb_array_length(top3) > 0
group by 1, 2, 3;

------------------------------------------------------------------------
-- 3. Anon má AÐEINS lesa aggregate-views (ekki undirliggjandi töflu)
------------------------------------------------------------------------
grant select on public.kompas_total_mv             to anon;
grant select on public.kompas_top1_counts_mv       to anon;
grant select on public.kompas_shoe_x_party_mv      to anon;
grant select on public.kompas_pool_x_party_mv      to anon;
grant select on public.kompas_archetype_x_party_mv to anon;

------------------------------------------------------------------------
-- 4. Trigger-fall sem refresh-ar öll MVs eftir hverja insert.
--    SECURITY DEFINER þarf til að refresh-a (krefst owner-réttinda),
--    en fallið er EKKI exposed í REST API af því anon hefur ekki EXECUTE.
------------------------------------------------------------------------
create or replace function public.refresh_kompas_aggregates()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  refresh materialized view public.kompas_total_mv;
  refresh materialized view public.kompas_top1_counts_mv;
  refresh materialized view public.kompas_shoe_x_party_mv;
  refresh materialized view public.kompas_pool_x_party_mv;
  refresh materialized view public.kompas_archetype_x_party_mv;
  return null;
end;
$$;

revoke execute on function public.refresh_kompas_aggregates() from public;
revoke execute on function public.refresh_kompas_aggregates() from anon;
revoke execute on function public.refresh_kompas_aggregates() from authenticated;

drop trigger if exists trg_refresh_kompas_aggregates on public.kompas_responses;
create trigger trg_refresh_kompas_aggregates
after insert on public.kompas_responses
for each statement
execute function public.refresh_kompas_aggregates();
