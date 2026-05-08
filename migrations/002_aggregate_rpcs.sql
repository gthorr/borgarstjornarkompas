-- Borgarstjórnar­kompás 2026 — opin RPC-föll fyrir lifandi tölfræðisíðu.
--
-- Mynstrið: föllin eru SECURITY DEFINER svo þau sjá undirliggjandi töflu, en þau
-- skila AÐEINS aggregated tölum (count + meðaltöl). Engin row-level gögn leka.
-- Þetta er rétt mynstur fyrir "anon má sjá heildargögn en ekki einstaklingsgögn".
--
-- Keyrðu þetta í SQL Editor á Supabase verkefninu.

------------------------------------------------------------------------
-- 1. Viðbót við töfluna: arketýpa-IDs sem appið sendir með hverri sub
------------------------------------------------------------------------
alter table public.kompas_responses
  add column if not exists archetype_ids text[];

------------------------------------------------------------------------
-- 2. Heildarfjöldi svara
------------------------------------------------------------------------
create or replace function public.get_total_responses()
returns int
language sql
stable
security definer
set search_path = public
as $$
  select count(*)::int from public.kompas_responses where consented = true;
$$;

------------------------------------------------------------------------
-- 3. Top-1 framboð: hve oft hvert framboð er efst
------------------------------------------------------------------------
create or replace function public.get_top1_counts()
returns table(list_letter text, party_name text, n int)
language sql
stable
security definer
set search_path = public
as $$
  select
    top3->0->>'code'        as list_letter,
    top3->0->>'short_name'  as party_name,
    count(*)::int           as n
  from public.kompas_responses
  where consented = true
    and top3 is not null
    and jsonb_array_length(top3) > 0
  group by 1, 2
  order by n desc;
$$;

------------------------------------------------------------------------
-- 4. Skóstærð × efsta framboð
------------------------------------------------------------------------
create or replace function public.get_shoe_x_party()
returns table(shoe_size text, list_letter text, party_name text, n int)
language sql
stable
security definer
set search_path = public
as $$
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
$$;

------------------------------------------------------------------------
-- 5. Uppáhalds laug × efsta framboð
------------------------------------------------------------------------
create or replace function public.get_pool_x_party()
returns table(laug text, list_letter text, party_name text, n int)
language sql
stable
security definer
set search_path = public
as $$
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
$$;

------------------------------------------------------------------------
-- 6. Persónugerð × efsta framboð
------------------------------------------------------------------------
create or replace function public.get_archetype_x_party()
returns table(archetype_id text, list_letter text, party_name text, n int)
language sql
stable
security definer
set search_path = public
as $$
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
$$;

------------------------------------------------------------------------
-- 7. Leyfa anon að kalla þessi RPC-föll
------------------------------------------------------------------------
grant execute on function public.get_total_responses()    to anon;
grant execute on function public.get_top1_counts()        to anon;
grant execute on function public.get_shoe_x_party()       to anon;
grant execute on function public.get_pool_x_party()       to anon;
grant execute on function public.get_archetype_x_party()  to anon;
