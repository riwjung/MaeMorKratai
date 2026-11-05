-- Apply once in a new Supabase project. No personal email addresses or secrets.
create table public.workshop_members (
  user_id uuid primary key references auth.users(id),
  role text not null check (role in ('owner','reader')),
  display_name text not null default '',
  active boolean not null default true
);
create table public.workshop_cases (
  id text primary key,
  version text not null,
  split text not null check (split in ('development','holdout'))
);
create table public.workshop_readings (
  reader_id uuid not null references public.workshop_members(user_id),
  case_id text not null references public.workshop_cases(id),
  revision integer not null default 0,
  stage text not null default 'baseline' check (stage in ('baseline','followup','review')),
  baseline jsonb not null default '{"answer":"","evidence":"","uncertainty":"","question":"","phrases":"","changes":"","unchanged":"","audioId":null}',
  followup jsonb not null default '{"answer":"","evidence":"","uncertainty":"","question":"","phrases":"","changes":"","unchanged":"","audioId":null}',
  updated_at timestamptz,
  primary key (reader_id,case_id)
);
create table public.workshop_responses (
  id uuid primary key,
  reader_id uuid not null,
  case_id text not null,
  revision integer not null,
  stage text not null,
  baseline jsonb not null,
  followup jsonb not null,
  created_at timestamptz not null default now(),
  case_version text not null,
  consent boolean not null check (consent),
  request jsonb not null,
  foreign key (reader_id,case_id) references public.workshop_readings on delete cascade,
  unique (reader_id,case_id,revision)
);
create table public.workshop_recordings (
  id uuid primary key,
  reader_id uuid not null,
  case_id text not null,
  stage text not null check (stage in ('baseline','followup')),
  object_key text not null unique,
  mime text not null check (mime in ('audio/webm','audio/mp4','audio/ogg','audio/wav')),
  bytes integer not null check (bytes between 32 and 16777216),
  duration integer not null check (duration between 0 and 600),
  status text not null default 'pending' check (status in ('pending','ready')),
  created_at timestamptz not null default now(),
  foreign key (reader_id,case_id) references public.workshop_readings on delete cascade
);
create table public.workshop_withdrawals (
  reader_id uuid primary key references public.workshop_members(user_id),
  requested_at timestamptz not null default now(),
  completed_at timestamptz
);

create function public.workshop_member_active(p_id uuid) returns boolean
language sql stable security definer set search_path='' as $$
  select exists(select 1 from public.workshop_members where user_id=p_id and active);
$$;
create function public.workshop_is_owner() returns boolean
language sql stable security definer set search_path='' as $$
  select exists(select 1 from public.workshop_members where user_id=auth.uid() and active and role='owner');
$$;
revoke all on function public.workshop_member_active(uuid), public.workshop_is_owner() from public;
grant execute on function public.workshop_member_active(uuid), public.workshop_is_owner() to authenticated;

alter table public.workshop_members enable row level security;
alter table public.workshop_cases enable row level security;
alter table public.workshop_readings enable row level security;
alter table public.workshop_responses enable row level security;
alter table public.workshop_recordings enable row level security;
alter table public.workshop_withdrawals enable row level security;
create policy members_read on public.workshop_members for select to authenticated
  using (user_id=auth.uid() or public.workshop_is_owner());
create policy cases_read on public.workshop_cases for select to authenticated
  using (public.workshop_member_active(auth.uid()));
create policy readings_read on public.workshop_readings for select to authenticated
  using (public.workshop_member_active(reader_id) and public.workshop_member_active(auth.uid())
    and (reader_id=auth.uid() or public.workshop_is_owner()));
create policy responses_read on public.workshop_responses for select to authenticated
  using (public.workshop_member_active(reader_id) and public.workshop_member_active(auth.uid())
    and (reader_id=auth.uid() or public.workshop_is_owner()));
create policy recordings_read on public.workshop_recordings for select to authenticated
  using (public.workshop_member_active(reader_id) and public.workshop_member_active(auth.uid())
    and (reader_id=auth.uid() or public.workshop_is_owner()));
create policy withdrawals_read on public.workshop_withdrawals for select to authenticated
  using (reader_id=auth.uid() or public.workshop_is_owner());
revoke all on public.workshop_members,public.workshop_cases,public.workshop_readings,
  public.workshop_responses,public.workshop_recordings,public.workshop_withdrawals from anon,authenticated;
grant select on public.workshop_members,public.workshop_cases,public.workshop_readings,
  public.workshop_responses,public.workshop_recordings,public.workshop_withdrawals to authenticated;
grant all on public.workshop_members,public.workshop_cases,public.workshop_readings,
  public.workshop_responses,public.workshop_recordings,public.workshop_withdrawals to service_role;

create function public.workshop_save(
  p_case text, p_request uuid, p_revision integer, p_stage text,
  p_action text, p_answers jsonb, p_consent boolean
) returns integer language plpgsql security definer set search_path='' as $$
declare
  who uuid := auth.uid(); r public.workshop_readings; prev public.workshop_responses;
  signature jsonb; nextstage text; field text; cv text;
begin
  if not public.workshop_member_active(who) then raise exception 'FORBIDDEN'; end if;
  if p_consent is distinct from true then raise exception 'CONSENT_REQUIRED'; end if;
  select version into cv from public.workshop_cases where id=p_case;
  if cv is null then raise exception 'CASE_NOT_FOUND'; end if;
  if p_revision is null or p_revision<0 or p_stage is null or p_action is null then raise exception 'INVALID_INPUT'; end if;
  if jsonb_typeof(p_answers) is distinct from 'object' then raise exception 'INVALID_INPUT'; end if;
  if (select count(*) from jsonb_object_keys(p_answers))<>8 then raise exception 'INVALID_INPUT'; end if;
  foreach field in array array['answer','evidence','uncertainty','question','phrases','changes','unchanged'] loop
    if jsonb_typeof(p_answers->field) is distinct from 'string' or length(p_answers->>field)>12000 then raise exception 'INVALID_INPUT'; end if;
  end loop;
  if not (p_answers ? 'audioId') or
    (p_answers->'audioId'<>'null'::jsonb and
     (jsonb_typeof(p_answers->'audioId') is distinct from 'string' or
      (p_answers->>'audioId') !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'))
    then raise exception 'INVALID_INPUT'; end if;
  signature := jsonb_build_object('revision',p_revision,'stage',p_stage,'action',p_action,'answers',p_answers);
  insert into public.workshop_readings(reader_id,case_id) values(who,p_case) on conflict do nothing;
  select * into r from public.workshop_readings where reader_id=who and case_id=p_case for update;
  select * into prev from public.workshop_responses where id=p_request;
  if found then
    if prev.reader_id<>who or prev.case_id<>p_case or prev.request<>signature then raise exception 'REQUEST_CONFLICT'; end if;
    return prev.revision;
  end if;
  if r.revision<>p_revision or r.stage<>p_stage or r.stage='review' then raise exception 'REVISION_CONFLICT'; end if;
  if p_action not in ('save','seal','submit') or
    (p_action='seal' and p_stage<>'baseline') or (p_action='submit' and p_stage<>'followup')
    then raise exception 'INVALID_ACTION'; end if;
  if p_action<>'save' and btrim(p_answers->>'answer')='' and p_answers->>'audioId' is null then raise exception 'ANSWER_REQUIRED'; end if;
  if p_answers->>'audioId' is not null and not exists(
    select 1 from public.workshop_recordings where id=(p_answers->>'audioId')::uuid
    and reader_id=who and case_id=p_case and stage=p_stage and status='ready'
  ) then raise exception 'AUDIO_NOT_READY'; end if;
  if p_stage='baseline' then r.baseline:=p_answers; else r.followup:=p_answers; end if;
  nextstage:=case p_action when 'seal' then 'followup' when 'submit' then 'review' else r.stage end;
  insert into public.workshop_responses(id,reader_id,case_id,revision,stage,baseline,followup,case_version,consent,request)
    values(p_request,who,p_case,r.revision+1,nextstage,r.baseline,r.followup,cv,true,signature);
  update public.workshop_readings set revision=r.revision+1,stage=nextstage,baseline=r.baseline,
    followup=r.followup,updated_at=now() where reader_id=who and case_id=p_case;
  return r.revision+1;
end;
$$;
revoke all on function public.workshop_save(text,uuid,integer,text,text,jsonb,boolean) from public;
grant execute on function public.workshop_save(text,uuid,integer,text,text,jsonb,boolean) to authenticated;

create function public.workshop_reserve_audio(p_id uuid,p_case text,p_stage text,p_mime text,p_bytes integer,p_duration integer)
returns public.workshop_recordings language plpgsql security definer set search_path='' as $$
declare who uuid:=auth.uid(); currentstage text; recording public.workshop_recordings;
begin
  if not public.workshop_member_active(who) then raise exception 'FORBIDDEN'; end if;
  if p_stage is null or p_stage not in ('baseline','followup') or p_mime is null or
    p_mime not in ('audio/webm','audio/mp4','audio/ogg','audio/wav') or
    p_bytes is null or p_bytes<32 or p_bytes>16777216 or p_duration is null or p_duration<0 or p_duration>600
    then raise exception 'INVALID_INPUT'; end if;
  insert into public.workshop_readings(reader_id,case_id) values(who,p_case) on conflict do nothing;
  select stage into currentstage from public.workshop_readings where reader_id=who and case_id=p_case for update;
  select * into recording from public.workshop_recordings where id=p_id;
  if found then
    if recording.reader_id<>who or recording.case_id<>p_case or recording.stage<>p_stage or
      recording.mime<>p_mime or recording.bytes<>p_bytes or recording.duration<>p_duration then raise exception 'REQUEST_CONFLICT'; end if;
    return recording;
  end if;
  if currentstage<>p_stage then raise exception 'REVISION_CONFLICT'; end if;
  insert into public.workshop_recordings(id,reader_id,case_id,stage,object_key,mime,bytes,duration)
    values(p_id,who,p_case,p_stage,who::text||'/'||p_id::text||'/'||gen_random_uuid()::text,p_mime,p_bytes,p_duration)
    returning * into recording;
  return recording;
end;
$$;
revoke all on function public.workshop_reserve_audio(uuid,text,text,text,integer,integer) from public;
grant execute on function public.workshop_reserve_audio(uuid,text,text,text,integer,integer) to authenticated;

-- Only the trusted server can finalize AFTER verifying the stored object.
create function public.workshop_complete_audio(p_id uuid,p_reader uuid) returns void
language plpgsql security definer set search_path='' as $$
declare recording public.workshop_recordings; currentstage text;
begin
  if not public.workshop_member_active(p_reader) then raise exception 'FORBIDDEN'; end if;
  select * into recording from public.workshop_recordings where id=p_id and reader_id=p_reader;
  if not found then raise exception 'AUDIO_NOT_READY'; end if;
  select stage into currentstage from public.workshop_readings where reader_id=p_reader and case_id=recording.case_id for update;
  if recording.status='ready' then return; end if;
  if currentstage<>recording.stage then raise exception 'REVISION_CONFLICT'; end if;
  update public.workshop_recordings set status='ready' where id=p_id;
end;
$$;
revoke all on function public.workshop_complete_audio(uuid,uuid) from public,anon,authenticated;
grant execute on function public.workshop_complete_audio(uuid,uuid) to service_role;

create function public.workshop_withdraw() returns void
language plpgsql security definer set search_path='' as $$
begin
  if not public.workshop_member_active(auth.uid()) then raise exception 'FORBIDDEN'; end if;
  if public.workshop_is_owner() then raise exception 'OWNER_WITHDRAW_REQUIRES_OPERATOR'; end if;
  insert into public.workshop_withdrawals(reader_id) values(auth.uid()) on conflict do nothing;
  update public.workshop_members set active=false where user_id=auth.uid();
end;
$$;
revoke all on function public.workshop_withdraw() from public;
grant execute on function public.workshop_withdraw() to authenticated;

-- The server mints upload/download tokens; there is intentionally no public
-- upload/list policy. Signed uploads never use upsert.
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
  values ('workshop-audio','workshop-audio',false,16777216,array['audio/webm','audio/mp4','audio/ogg','audio/wav']);
