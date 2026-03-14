create database bilibili;


create table tasks_to_do(
"uid" text,
"av" text not null,
"status" int not null ,
"url" text primary key,
"video_path" text,
"created_time" timestamp not null default CURRENT_TIMESTAMP,
"error_msg" text
);
comment on column tasks_to_do.status is '0 init,1 download start,2 download done,3 split wave done,4 stt done,5 indexed done';