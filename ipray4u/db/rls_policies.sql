-- people
create policy "Users can view own people"
on public.people
for select
to authenticated
using (
    user_id = auth.uid()
);

create policy "Users can insert own people"
on public.people
for insert
to authenticated
with check (
    user_id = auth.uid()
);

create policy "Users can update own people"
on public.people
for update
to authenticated
using (
    user_id = auth.uid()
)
with check (
    user_id = auth.uid()
);

create policy "Users can delete own people"
on public.people
for delete
to authenticated
using (
    user_id = auth.uid()
);

-- prayers
create policy "Users can view own prayers"
on public.prayers
for select
to authenticated
using (
    exists (
        select 1
        from public.people
        where people.id = prayers.person_id
          and people.user_id = auth.uid()
    )
);

create policy "Users can insert own prayers"
on public.prayers
for insert
to authenticated
with check (
    exists (
        select 1
        from public.people
        where people.id = prayers.person_id
          and people.user_id = auth.uid()
    )
);

create policy "Users can update own prayers"
on public.prayers
for update
to authenticated
using (
    exists (
        select 1
        from public.people
        where people.id = prayers.person_id
          and people.user_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.people
        where people.id = prayers.person_id
          and people.user_id = auth.uid()
    )
);

create policy "Users can delete own prayers"
on public.prayers
for delete
to authenticated
using (
    exists (
        select 1
        from public.people
        where people.id = prayers.person_id
          and people.user_id = auth.uid()
    )
);

-- profiles
create policy "Users can view own profile"
on public.profiles
for select
to authenticated
using (
    id = auth.uid()
);

create policy "Users can insert own profile"
on public.profiles
for insert
to authenticated
with check (
    id = auth.uid()
);

create policy "Users can update own profile"
on public.profiles
for update
to authenticated
using (
    id = auth.uid()
)
with check (
    id = auth.uid()
);

-- relationships
create policy "Authenticated users can view relationships"
on public.relationships
for select
to authenticated
using (
    true
);
