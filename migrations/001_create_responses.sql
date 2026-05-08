-- Borgarstjórnar­kompás 2026 — nafnlaus svaratafla
-- Keyrðu þetta í SQL Editor á Supabase verkefninu þínu.

create table if not exists public.kompas_responses (
  id                 uuid primary key default gen_random_uuid(),
  created_at         timestamptz not null default now(),
  client_session     uuid,
  consented          boolean not null,
  answers_likert     jsonb not null,
  answers_chaos      jsonb not null default '{}'::jsonb,
  top3               jsonb not null,
  user_axis_vector   jsonb not null,
  evidence_summary   jsonb,
  app_version        text default '1.0'
);

create index if not exists kompas_responses_created_at_idx
  on public.kompas_responses (created_at desc);

-- Defense-in-depth: anon key má AÐEINS setja inn raðir þar sem consented = true.
-- Engin lestur leyfður með anon key — notið service_role key fyrir greiningu.
alter table public.kompas_responses enable row level security;

drop policy if exists "anon_insert_consented_only" on public.kompas_responses;
create policy "anon_insert_consented_only"
  on public.kompas_responses
  for insert
  to anon
  with check (consented = true);

drop policy if exists "no_anon_read" on public.kompas_responses;
create policy "no_anon_read"
  on public.kompas_responses
  for select
  to anon
  using (false);

-- Yfirlitsskoðun fyrir greiningu.
-- security_invoker = true: view notar permissions kallandans (ekki creators).
-- Það þýðir að anon-key-kall fær engan aðgang (af því RLS á töflunni neitar
-- anon-lestri), en service_role kall sér allt.
drop view if exists public.kompas_top3_aggregate;
create view public.kompas_top3_aggregate
  with (security_invoker = true)
as
select
  t.value ->> 'code'                                    as list_letter,
  count(*)                                              as picks,
  round(avg((t.value ->> 'match_percent')::numeric), 1) as avg_match_pct
from public.kompas_responses r
cross join lateral jsonb_array_elements(r.top3) as t
where r.consented = true
group by 1
order by picks desc;
