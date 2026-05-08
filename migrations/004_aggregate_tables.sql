-- Borgarstjórnar­kompás 2026 — síðasta umferð á aggregate-laginu.
--
-- Skiptum úr materialized views yfir í venjulegar töflur sem trigger-fall
-- TRUNCATE-ar og INSERT-ar gögnum í eftir hverja insert á kompas_responses.
-- Anon má SELECT á þessar töflur (RLS leyfir það) en sér engin row-level
-- gögn úr undirliggjandi kompas_responses.
--
-- Þessi nálgun hreinsar Supabase-linter #0016 (materialized view in API).

------------------------------------------------------------------------
-- 1. Eldra MV-lag burt
------------------------------------------------------------------------
drop trigger if exists trg_refresh_kompas_aggregates on public.kompas_responses;
drop function if exists public.refresh_kompas_aggregates();

drop materialized view if exists public.kompas_total_mv cascade;
drop materialized view if exists public.kompas_top1_counts_mv cascade;
drop materialized view if exists public.kompas_shoe_x_party_mv cascade;
drop materialized view if exists public.kompas_pool_x_party_mv cascade;
drop materialized view if exists public.kompas_archetype_x_party_mv cascade;

------------------------------------------------------------------------
-- 2. Aggregate-töflur
------------------------------------------------------------------------
create table if not exists public.kompas_total (
  total int not null
);

create table if not exists public.kompas_top1 (
  list_letter  text,
  party_name   text,
  n            int not null
);

create table if not exists public.kompas_shoe_x_party (
  shoe_size    text,
  list_letter  text,
  party_name   text,
  n            int not null
);

create table if not exists public.kompas_pool_x_party (
  laug         text,
  list_letter  text,
  party_name   text,
  n            int not null
);

create table if not exists public.kompas_archetype_x_party (
  archetype_id text,
  list_letter  text,
  party_name   text,
  n            int not null
);

------------------------------------------------------------------------
-- 3. RLS — anon má AÐEINS lesa þessar aggregate-töflur
------------------------------------------------------------------------
alter table public.kompas_total              enable row level security;
alter table public.kompas_top1               enable row level security;
alter table public.kompas_shoe_x_party       enable row level security;
alter table public.kompas_pool_x_party       enable row level security;
alter table public.kompas_archetype_x_party  enable row level security;

drop policy if exists "anon_select" on public.kompas_total;
create policy "anon_select" on public.kompas_total
  for select to anon using (true);

drop policy if exists "anon_select" on public.kompas_top1;
create policy "anon_select" on public.kompas_top1
  for select to anon using (true);

drop policy if exists "anon_select" on public.kompas_shoe_x_party;
create policy "anon_select" on public.kompas_shoe_x_party
  for select to anon using (true);

drop policy if exists "anon_select" on public.kompas_pool_x_party;
create policy "anon_select" on public.kompas_pool_x_party
  for select to anon using (true);

drop policy if exists "anon_select" on public.kompas_archetype_x_party;
create policy "anon_select" on public.kompas_archetype_x_party
  for select to anon using (true);

------------------------------------------------------------------------
-- 4. Helper sem TRUNCATE-ar og INSERT-ar aggregates (notað af trigger og seeding)
------------------------------------------------------------------------
create or replace function public._kompas_recompute_aggregates()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from public.kompas_total;
  insert into public.kompas_total (total)
    select count(*)::int from public.kompas_responses where consented = true;

  delete from public.kompas_top1;
  insert into public.kompas_top1 (list_letter, party_name, n)
    select
      top3->0->>'code',
      top3->0->>'short_name',
      count(*)::int
    from public.kompas_responses
    where consented = true
      and top3 is not null
      and jsonb_array_length(top3) > 0
    group by 1, 2;

  delete from public.kompas_shoe_x_party;
  insert into public.kompas_shoe_x_party (shoe_size, list_letter, party_name, n)
    select
      answers_chaos->>'c01_skostaerd',
      top3->0->>'code',
      top3->0->>'short_name',
      count(*)::int
    from public.kompas_responses
    where consented = true
      and answers_chaos ? 'c01_skostaerd'
      and answers_chaos->>'c01_skostaerd' is not null
      and top3 is not null
      and jsonb_array_length(top3) > 0
    group by 1, 2, 3;

  delete from public.kompas_pool_x_party;
  insert into public.kompas_pool_x_party (laug, list_letter, party_name, n)
    select
      answers_chaos->>'c02_uppahalds_laug',
      top3->0->>'code',
      top3->0->>'short_name',
      count(*)::int
    from public.kompas_responses
    where consented = true
      and answers_chaos ? 'c02_uppahalds_laug'
      and answers_chaos->>'c02_uppahalds_laug' is not null
      and top3 is not null
      and jsonb_array_length(top3) > 0
    group by 1, 2, 3;

  delete from public.kompas_archetype_x_party;
  insert into public.kompas_archetype_x_party (archetype_id, list_letter, party_name, n)
    select
      unnest(archetype_ids),
      top3->0->>'code',
      top3->0->>'short_name',
      count(*)::int
    from public.kompas_responses
    where consented = true
      and archetype_ids is not null
      and array_length(archetype_ids, 1) > 0
      and top3 is not null
      and jsonb_array_length(top3) > 0
    group by 1, 2, 3;
end;
$$;

revoke execute on function public._kompas_recompute_aggregates() from public;
revoke execute on function public._kompas_recompute_aggregates() from anon;
revoke execute on function public._kompas_recompute_aggregates() from authenticated;

------------------------------------------------------------------------
-- 5. Trigger-fall
------------------------------------------------------------------------
create or replace function public.refresh_kompas_aggregates()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  perform public._kompas_recompute_aggregates();
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

------------------------------------------------------------------------
-- 6. Initial seed (svo við byrjum með núverandi gögn í aggregate-töflunum)
------------------------------------------------------------------------
select public._kompas_recompute_aggregates();
