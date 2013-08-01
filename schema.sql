drop table if exists schools;
create table schools (
    id integer primary key autoincrement,
    name text not null
);

drop table if exists periods;
create table periods (
    school_id integer not null,
    period_name text not null,
    start_time time not null,
    end_time time not null
);


drop table if exists letter_days;
create table letter_days (
    school_id integer not null,
    day_name text not null,
    display_order integer default 0
);


drop table if exists dates_days;
create table dates_days (
    school_id integer not null,
    day_name text not null,
    date date not null
);

